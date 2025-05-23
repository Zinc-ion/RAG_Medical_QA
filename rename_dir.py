import os
def rename_dir(work_dir, old_ext, new_ext):
    # old_ext, new_ext = '.docx', '.txt'
    for filename in os.listdir(work_dir):
        # 获取得到文件后缀
        split_file = os.path.splitext(filename)
        file_ext = split_file[1]  # 把所有文件属性(.docx/.txt)赋给file_ext

        if old_ext == file_ext:  # 如果文件属性是 .docx 执行
            newfile = split_file[0] + new_ext  # 修改后的文件完整名称
            os.rename(  # 实现重命名操作
                os.path.join(work_dir, filename),  # 文件路径不变
                os.path.join(work_dir, newfile))  # 文件后缀变为 [new_ext]值
        print("完成重命名")
    print(os.listdir(work_dir))  # 打印修改后文件信息
    return


rename_dir("/doc/medical-books/01已经抽取完毕的资料/药理学//content", ".tex", ".txt")
