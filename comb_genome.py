import os
import itertools
import argparse
from collections import defaultdict, Counter

#setting output filename
OUTPUT_FILE_NAME = "combition_results.txt"

class CombitonGenome:
    """
    生成不同目录的基因组组合, 并将组合写入指定文件， 输出文件为 combition_all.txt

    Options:
        --genome_dir: 基因组存放目录

        --out_dir: 指定结果输出路径, 无需提前创建

        --run_mode: 两种运行模式: (1) all: 输出所有组合  (2)fix: 输出固定数量的组合数, 具体组合
数由 --n 选项指定

        --n: 生成指定的组合数量, 如两两组合指定为 --n 2

    Usage:
        生成两两组合
        python comb_genome.py \
            --genome_dir ./test_genome \
            --out_dir ./test \
            --run_mode fix \
            --n 2

        生成全部组合
        python comb_genome.py \
            --genome_dir ./test_genome \
            --out_dir ./test \
            --run_mode all

    """
    def __init__(self, genome_dir, run_mode, out_dir, n = None):
        self.genome_dir = genome_dir
        self.merge_cmd_all = []

        if os.path.exists(out_dir):
            self.out_dir = os.path.abspath(out_dir)
        else:
            abs_path = os.path.abspath(out_dir)
            os.system(f"mkdir -p {abs_path}")
            self.out_dir = abs_path

        self.combition_count = 1
        self.run_mode = run_mode
        if self.run_mode not in ["all", "fix"]:
            raise Exception("invalid option")
        self.n = n

    def get_dir_genome_dict(self):
        """
        return
        {genome_dir1:[f1.xml, f2.xml, f3.xml], genome_dir3:[f4.xml, f5.xml]...}
        """
        dir_genome_dict = defaultdict(list)
        dir_list = os.listdir(self.genome_dir)
        for dir in dir_list:
            dir_genome_dict[dir] = os.listdir(f"{self.genome_dir}/{dir}")
        self.dir_genome_dict = dir_genome_dict

    def get_all_genome_name(self):
        """return all genome name in a list
        [f1.xml, f2.xml, f3.xml, f4.xml....]
        """
        all_genome_list  = []
        for _, v in self.dir_genome_dict.items():
            all_genome_list += v
        self.all_genome_list = all_genome_list

    def get_all_combition(self):
        """
        return all combition of genome
        """
        n_combition = len(self.all_genome_list)
        for n in range(1, n_combition + 1):
            genome_combition  = itertools.combinations(self.all_genome_list, n)
            self._write_to_txt(genome_combition)

    def get_n_combition(self):
        """
        return combition of genome
        """
        if self.n > len(self.all_genome_list):
            self.n = len(self.all_genome_list)
        genome_combition  = itertools.combinations(self.all_genome_list, self.n)
        self._write_to_txt(genome_combition)


    def _write_to_txt(self, iter):
        """
        write combition info to a tsv file
        """
        for comb in iter:
            flag = self._if_filter_conbition(comb)
            if flag == 1:
                comb_lst = []
                for xml in comb:
                    with open(f"{self.out_dir}/{OUTPUT_FILE_NAME}", "a") as fd:
                        fd.write(f"combition_{self.combition_count}\t{xml}\n")
                        comb_lst.append(xml)
                # merge cmd
                cmd = f'merge_community {" ".join(comb_lst)} -o combition_{self.combition_count}.xml'
                self.merge_cmd_all.append(cmd)
                self.combition_count += 1


    def _get_genome_dir(self, genome_name):
        for k, v in self.dir_genome_dict.items():
            if genome_name in v:
                return k
    def _if_filter_conbition(self, comb):
        """
        filter genome combition 去掉所有同一个文件夹出现的组合
        args:
            comb: 不同的组合情况, 如 (f1.xml, f3.xml, f4.xml...)
        """
        dir_list = []
        for elm in comb:
            dir_list.append(self._get_genome_dir(elm))
         #去掉or len(dir_list) == 1 可以保留只有一个基因组的组合
        if len(set(dir_list)) !=  len(dir_list) or len(dir_list) == 1:
            return 0
        else:
            return 1


    def write_smetana_sh(self):
        with open(f"{self.out_dir}/run_smetana.sh", "w") as fd:
            fd.write(f"smetana *.xml -c {self.out_dir}/{OUTPUT_FILE_NAME}")

    def write_merge_sh(self):
        with open(f"{self.out_dir}/merge.sh", "w") as fd:
            for cmd in self.merge_cmd_all:
                fd.write(f"{cmd}\n")

    def run(self):
        self.get_dir_genome_dict()
        self.get_all_genome_name()
        if self.run_mode == "all":
            self.get_all_combition()
        elif self.run_mode == "fix":
            self.get_n_combition()
        self.write_smetana_sh()
        self.write_merge_sh()



def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("--genome_dir", help = "", required = True)
    arg.add_argument("--out_dir", help = "", required = True)
    arg.add_argument("--run_mode", help = "", required = True)
    arg.add_argument("--n", help = "", default = 3)
    args = arg.parse_args()

    target = CombitonGenome(
        genome_dir = args.genome_dir,
        out_dir = args.out_dir,
        run_mode = args.run_mode,
        n = int(args.n)
    )
    target.run()


if __name__ == "__main__":
    main()
