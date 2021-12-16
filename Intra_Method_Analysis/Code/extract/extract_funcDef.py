import ast
from Intra_Method_Analysis.Code.extract.submodule.get_nodeNames import get_Call_Name
from Intra_Method_Analysis.Code.extract.submodule.get_funcArgs import parse_function_arguments

class FuncDefExtractor(ast.NodeVisitor):
    def __init__(self, script):
        self.funcStats = {
            "name": [],  # 当前文件内定义的函数名列表, [name1, name2, ...]
            "args": [],  # 函数参数, [[1's arg], [2's arg], ...]
            "APIs": [],  # 函数中调用的API列表, [[f1_api_1, f1_api_2, ...], ...]
            "lineNo": [],  # 每个被调用API的起始行号, [[f1_line_1, f1_line_2, ...], ...]
            "end_lineNo": [],  # 每个被调用API的结束行号，用于应对API跨行的Case
            "variables": [],
            "check_table": []
        }
        self.APIs = []
        self.lines = []
        self.end_lines = []
        self.variables = []  # 记录每个函数中被定义的变量
        self.check_table = []
        self.isInFunc = False
        self.script = script

    def visit_FunctionDef(self, node):
        """
        解析函数定义
        我们做的是函数内解析，所以这算是解析入口
        """
        self.isInFunc = True
        self.generic_visit(node)
        self.funcStats["APIs"].append(self.APIs)
        self.APIs = []
        self.funcStats["lineNo"].append(self.lines)
        self.lines = []
        self.funcStats["end_lineNo"].append(self.end_lines)
        self.end_lines = []
        self.funcStats["variables"].append(self.variables)
        self.variables = []
        self.funcStats["check_table"].append(self.check_table)
        self.check_table = []
        self.funcStats["name"].append(node.name)
        args = parse_function_arguments(node)  # 解析获取函数的参数信息
        self.funcStats["args"].append(args)
        self.isInFunc = False

    def visit_Call(self, node):
        if self.isInFunc:
            self.generic_visit(node)
            name = get_Call_Name(node, '')
            if name != '' and name is not None:
                self.APIs.append(name[:-1])
                self.lines.append(node.lineno)
                self.end_lines.append(node.end_lineno)
            else:
                pass
        else:
            pass

    def visit_Lambda(self, node):
        """
        因为lambda表达式执行顺序在运行时才能确定，
        为了不引入错误，所以不处理lambda表达式
        """
        pass

    def visit_Assign(self, node):
        """
        解析Assign结点是为了得到方法内定义的所有变量
        """
        if self.isInFunc:
            self.generic_visit(node)
            for target in node.targets:
                if isinstance(node.value, ast.Call):
                    if isinstance(target, ast.Name):
                        nodeName = get_Call_Name(node.value, '')
                        if nodeName is not None:
                            self.check_table.append([target.id, nodeName[:-1], target.lineno])  # target.id是nodeName的别名
                            self.variables.append([target.lineno, target.end_lineno, target.col_offset, target.end_col_offset, target.id, get_Call_Name(node.value, '')])
                        else:
                            continue
                    elif isinstance(target, ast.Tuple):
                        # print('Tuple:', target.lineno, target.end_lineno)
                        continue
                    else:
                        continue
                elif isinstance(node.value, ast.BinOp):
                    if isinstance(node.value.left, ast.Call) or isinstance(node.value.right, ast.Call):
                        # print('BinOp:', target.lineno, target.end_lineno)
                        continue
                    else:
                        continue
                else:
                    continue
        else:
            pass


    def report(self):
        with open('/Users/abnerallen/Documents/API_Misuse/python_mine/Python_Analyze/Intra_Method_Analysis/Resource/result.txt', 'a') as f:
            for i in range(len(self.funcStats["name"])):  # 一个源文件中可能定义多个函数
                f.write(self.funcStats["name"][i])  # 第i个函数的名字
                f.write(':\n')
                for subs in range(len(self.funcStats["APIs"][i])):  # 第i个函数中有若干API调用
                    if self.funcStats["APIs"][i][subs] is not None:
                        f.write(self.funcStats["APIs"][i][subs])
                        f.write(' ')
                        f.write(str(self.funcStats["lineNo"][i][subs]))
                        f.write(' ')
                        f.write(str(self.funcStats["end_lineNo"][i][subs]))
                        f.write('\n')
                    else:
                        continue
                f.write('\n')
            f.write('--------------------------------------------\n\n')
