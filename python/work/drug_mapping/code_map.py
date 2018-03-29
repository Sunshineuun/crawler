# coding=utf8
import pandas as pd
import re
from pypinyin import pinyin, lazy_pinyin


class CodeMap:
    def __init__(self):
        self.path = 'e:\\share\\kbms_drug_dict.txt'
        self.is_delete = 'e:\\share\\is_delete.txt'
        self.usual_name = 'e:\\share\\bieming_test.txt'  # 别名存储
        self.memory_name = 'e:\\share\\memory_match.txt'
        self.row_data = []
        self.alias = []
        self.memory_dict = []
        self.df_raw = None

    def get_alias(self):
        """
        获取别名字典
        :return:
        """
        l_name = []
        r_name = []
        f = open(self.usual_name, encoding='utf8')
        for i in f:
            i = i.replace('\n', '')
            temp = i.split(' ')
            l_name.append(temp[0])
            r_name.append(temp[1])
            l_name.append(temp[1])
            r_name.append(temp[0])
        f.close()
        return list(zip(l_name, r_name))

    def get_memory_dict(self):
        """
        创建一个内存形态的表【pandas】
        与【get_rawcode】类似
        :return:
        """
        # 临时字典
        temp_dict = []
        f = open(self.memory_name, encoding='utf8')
        # 读取数据将数据存入字典中
        for i in f:
            if re.findall('D[RSL]', i):
                temp_dict.append(i.replace('\n', '').split(' ')[0:5])

        # 使用pandas将list做成一个表
        self.memory_dict = pd.DataFrame(temp_dict)
        # 表头，或者认为是表的列索引名称
        self.memory_dict.columns = ['PRODUCT_NAME', 'TRAD_NAME', 'DRUG_FORM', 'GENERIC_NAME', 'LEVEL1']
        # 拷贝LEVEL1到LEVEL2，LEVEL3
        self.memory_dict['LEVEL2'] = self.memory_dict.LEVEL1
        self.memory_dict['LEVEL3'] = self.memory_dict.LEVEL1
        f.close()

    def get_rawcode(self):
        """
        创建一个内存形态的表，
        与【get_memory_dict】类似
        :return:
        """
        id = 0
        f = open(self.path, encoding='utf8')
        for i in f:
            # i=i.replace('\n','')
            # i=i.replace('-')
            # i=re.sub('[?？，;\'><&\(\)（）。!#*.]','',i)
            i = re.sub('[\s\-\n]', '', i)  # 替换掉空白符，tab符号，换行符号，-符号
            temp_dict = {}
            # id==0，说明是第一行，为列头
            if id == 0:
                col = i.split(',')
            elif id > 0:
                for j in range(len(col)):
                    temp_dict[col[j]] = i.split(',')[j]
                self.row_data.append(temp_dict)

            id = id + 1
        f.close()
        # 一个dataframe是一个二维的表结构
        self.df_raw = pd.DataFrame(self.row_data)
        self.row_data = []
        return self.df_raw

    def full_match_l1(self, name1=None, name2=None, name3=None, form_drug=None):
        """
        规则1 product_name
        :param name1:
        :param name2:
        :param name3:
        :param form_drug:
        :return:
        """
        if form_drug is None:
            form_drug = ''
        # shape函数返回一个元素(多少行,多少列)
        if self.df_raw[self.df_raw.PRODUCT_NAME == name1].shape[0] > 0:
            # 返回二维表中产品名称与name1相等数据
            return self.df_raw[self.df_raw.PRODUCT_NAME == name1]
        elif self.df_raw[self.df_raw.PRODUCT_NAME == name2].shape[0] > 0:
            # 返回二维表中产品名称与name2相等数据
            return self.df_raw[self.df_raw.PRODUCT_NAME == name2]
        elif self.df_raw[self.df_raw.PRODUCT_NAME == name3].shape[0] > 0:
            # 同上
            return self.df_raw[self.df_raw.PRODUCT_NAME == name3]
        elif self.df_raw[self.df_raw.PRODUCT_NAME == name1 + form_drug].shape[0] > 0:
            # 产品名称 == 名称+剂型
            return self.df_raw[self.df_raw.PRODUCT_NAME == name1 + form_drug]
        elif form_drug is not None and self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name1) \
                & (self.df_raw.ACTUAL_FORM_CODE == form_drug)].shape[0] > 0:
            # 小通用名+实际剂型==name1+剂型
            return self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name1) \
                               & (self.df_raw.ACTUAL_FORM_CODE == form_drug)]
        elif form_drug is not None and self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name2) \
                & (self.df_raw.ACTUAL_FORM_CODE == form_drug)].shape[0] > 0:
            # 小通用名+实际剂型==name2+剂型
            return self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name2) \
                               & (self.df_raw.ACTUAL_FORM_CODE == form_drug)]
        elif form_drug is not None and self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name3) \
                & (self.df_raw.ACTUAL_FORM_CODE == form_drug)].shape[0] > 0:
            # 小通用名+实际剂型==name3+剂型
            return self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name3) \
                               & (self.df_raw.ACTUAL_FORM_CODE == form_drug)]
        else:
            return self.df_raw[self.df_raw.SMALL_GENERIC_NAME == '*****']

    def full_match_l2(self, name1=None, name2=None, name3=None, form_drug=None):
        """
        小通用名+标注剂型
        :param name1:
        :param name2:
        :param name3:
        :param form_drug:
        :return:
        """
        if form_drug is not None and self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name1) \
                & (self.df_raw.LABEL_FORM_NAME == form_drug)].shape[0] > 0:
            # 小通用名+标注剂型
            return self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name1) \
                               & (self.df_raw.LABEL_FORM_NAME == form_drug)]
        elif form_drug is not None and self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name2) \
                & (self.df_raw.LABEL_FORM_NAME == form_drug)].shape[0] > 0:
            return self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name2) \
                               & (self.df_raw.LABEL_FORM_NAME == form_drug)]
        elif form_drug is not None and self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name3) \
                & (self.df_raw.LABEL_FORM_NAME == form_drug)].shape[0] > 0:
            return self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name3) \
                               & (self.df_raw.LABEL_FORM_NAME == form_drug)]
        else:
            return self.df_raw[self.df_raw.PRODUCT_NAME == '****']

    def full_match_l3(self, name1=None, name2=None, name3=None):
        """
        小通用名
        :param name1:
        :param name2:
        :param name3:
        :return:
        """
        if self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name1)].shape[0] > 0:
            # 小通用名
            return self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name1)]

        elif self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name2)].shape[0] > 0:
            return self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name2)]

        elif self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name3)].shape[0] > 0:
            return self.df_raw[(self.df_raw.SMALL_GENERIC_NAME == name3)]
        else:
            return self.df_raw[self.df_raw.PRODUCT_NAME == '****']

    # def memory_match(self,name1=None,name2=None,name3=None,form_drug=None):

    def rule_1(self, name1=None, name2=None, name3=None, form_drug=None):
        """
        商品名称
        :param name1:
        :param name2:
        :param name3:
        :param form_drug:
        :return:
        """
        product_name = [name1, name2, name3]
        return self.df_raw[self.df_raw.TRAD_NAME.isin(product_name)]

    def rule_2(self, name1=None, name2=None, name3=None, form_drug=None):
        """
        剔除无效字符，进行查找 \n
        1.[?？，;'><&()（）。!#*.] \n
        2.将中文，罗马数字替换为阿拉伯数字 \n
        3.并且对二位表中self.df_raw.PRODUCT_NAME进行对比获取匹配的值 \n
        :param name1:
        :param name2:
        :param name3:
        :param form_drug:
        :return: 查到的结果
        """
        cn_num = '一二三四五六七八九'
        r_cn_num = '[一二三四五六七八九]'
        num = '123456789'
        r_num = '[123456789]'
        roman_num = 'ⅠⅡⅢⅣⅤⅥⅦⅧⅨ'
        r_roman_num = '[ⅠⅡⅢⅣⅤⅥⅦⅧⅨ]'

        product_name = []
        names = [name1, name2, name3]
        for name in names:
            if name is not None:
                # 替换特殊字符
                name = re.sub('[\?？，;\'><&\(\)（）。!#*.]', '', name)

                # 将数字替换为阿拉伯数字
                if re.findall(r_cn_num, name):
                    for sn in range(len(cn_num)):
                        name = re.sub(cn_num[sn], num[sn], name)
                if re.findall(r_roman_num, name):
                    for sn in range(len(cn_num)):
                        name = re.sub(roman_num[sn], num[sn], name)

                """
                对二维表中的product_name列进行替换数字，然后进行比较如果相等则加入到返回队列中
                """
                for t_pn in self.df_raw.PRODUCT_NAME:
                    source = t_pn
                    if re.findall('[一二三四五六七八九123456789ⅠⅡⅢⅣⅤⅥⅦⅧⅨ]', t_pn):
                        for sn in range(len(cn_num)):
                            t_pn = re.sub(cn_num[sn], num[sn], t_pn)
                        for sn in range(len(cn_num)):
                            t_pn = re.sub(roman_num[sn], num[sn], t_pn)
                        # print(j)
                        if name == t_pn:
                            product_name.append(source)

        data = self.df_raw[self.df_raw.PRODUCT_NAME.isin(product_name)]
        if data.shape[0] > 0:
            return data
        else:
            return self.df_raw[self.df_raw.SMALL_GENERIC_NAME.isin(product_name)]

    def rule_3(self, name1=None, name2=None, name3=None, form_drug=None):
        """
        1.替换【\d*\.?\d*\%】 \n
        2.名称包含比例
        3.0.9%氯化钠
        :param name1:
        :param name2:
        :param name3:
        :param form_drug:
        :return: 返回匹配结果
        """
        product_name = []
        names = [name1, name2, name3]

        for name in names:
            if name is not None:
                if re.findall('\d*\.?\d*\%', name):
                    n = re.sub('\d*\.?\d*\%', '', name)
                    if self.df_raw[self.df_raw.PRODUCT_NAME == n].shape[0] > 0:
                        product_name.append(n)

        data = self.df_raw[self.df_raw.PRODUCT_NAME.isin(product_name)]
        if data.shape[0] > 0:
            return data
        else:
            return self.df_raw[self.df_raw.SMALL_GENERIC_NAME.isin(product_name)]

    def rule_4(self, name1=None, name2=None, name3=None, form_drug=None):
        """
        1.产品名称处理多音字的情况 \n
        2.拼音码+象形字 \n
        3.名称包含错别字
        :param name1:
        :param name2:
        :param name3:
        :param form_drug:
        :return:
        """
        product_name = []
        names = [name1, name2, name3]

        for name in names:
            if name is not None:
                py_name = lazy_pinyin(name)
                for i in self.df_raw.PRODUCT_NAME:
                    if lazy_pinyin(i) == py_name:
                        if self.df_raw[self.df_raw.PRODUCT_NAME == i].shape[0] > 0:
                            product_name.append(i)

        data = self.df_raw[self.df_raw.PRODUCT_NAME.isin(product_name)]
        if data.shape[0] > 0:
            return data
        else:
            return self.df_raw[self.df_raw.SMALL_GENERIC_NAME.isin(product_name)]

    def rule_5(self, name1=None, name2=None, name3=None, form_drug=None):
        """
        1.替换特殊字符【* ? ？ 空白格 - _ + # & @符号】 \n
        2.特殊字符位置不变，精准匹配，提供特殊字符集 \n
        3.利用偏移位置进行处理。
        :param name1:
        :param name2:
        :param name3:
        :param form_drug:
        :return:
        """
        product_name = []
        names = [name1, name2, name3]

        for name in names:
            if name is not None:
                pos = re.search('[\*\?？\s -_+\#\&@]', name)
                temp_name = re.sub('[\*\?？\s -_+\#\&@]', '', name)
                if pos:
                    for j in self.df_raw.PRODUCT_NAME:
                        if len(j) == len(name) and j[0:pos.start()] + j[pos.end():len(j)] == temp_name:
                            product_name.append(j)

        data = self.df_raw[self.df_raw.PRODUCT_NAME.isin(product_name)]
        if data.shape[0] > 0:
            return data
        else:
            return self.df_raw[self.df_raw.SMALL_GENERIC_NAME.isin(product_name)]

    def rule_6(self, name1=None, name2=None, name3=None, form_drug=None):
        """
        1.异常字符 \n
        2.替换异常字符，然后进行匹配。 \n
        :param name1:
        :param name2:
        :param name3:
        :param form_drug:
        :return:
        """
        product_name = []
        names = [name1, name2, name3]
        for name in names:
            if name is not None and re.findall('[A-Z0-9\.\*\?\？\-%,。（\+\-）\(\)]', name1):
                name = re.sub('[A-Z0-9\.\*\?\？\-%,。（\+\-）\(\)]', '', name1)
                for j in self.df_raw.PRODUCT_NAME:
                    if name == re.sub('[A-Z0-9\.\*\?\？\-%,。（\+\-）\(\)]', '', j):
                        product_name.append(j)

        data = self.df_raw[self.df_raw.PRODUCT_NAME.isin(product_name)]
        if data.shape[0] > 0:
            return data
        else:
            return self.df_raw[self.df_raw.SMALL_GENERIC_NAME.isin(product_name)]

    def rule_8(self, name1=None, name2=None, name3=None, form_drug=None):
        """
        名称带括号,三级
        :param name1:
        :param name2:
        :param name3:
        :param form_drug:
        :return:
        """
        product_name = []
        names = [name1, name2, name3]
        for name in names:
            if name is not None:
                text = re.search('[\(|（][\s\S]*?[\)|）]', name)
                if text:
                    del_text = text.group()
                    product_name.append(name.replace(del_text, ''))

        data = self.df_raw[self.df_raw.PRODUCT_NAME.isin(product_name)]
        if data.shape[0] > 0:
            return data
        else:
            return self.df_raw[self.df_raw.SMALL_GENERIC_NAME.isin(product_name)]

    def rule_11(self, name1=None, name2=None, name3=None, form_drug=None):
        ###曾经用名
        bieming_dict = self.get_alias()

        bieming_check = [j[0] for j in bieming_dict if j[1] == name1]
        data = self.df_raw[self.df_raw.PRODUCT_NAME.isin(bieming_check)]

        if data.shape[0] > 0:
            return data
        else:
            return self.df_raw[self.df_raw.SMALL_GENERIC_NAME.isin(bieming_check)]

    def rule_12(self, name1=None, name2=None, name3=None, form_drug=None):
        ###名字位置调换
        similiar_name = []
        if name1 == None:
            name1 = name2
        if (name1 == None) & (name2 == None):
            name1 = name3
        for i in self.df_raw.PRODUCT_NAME:
            if len(i) == len(name1):
                temp = [character for character in name1 if character in list(i)]
                if len(temp) == len(name1):
                    similiar_name.append(temp)
        return self.df_raw[self.df_raw.PRODUCT_NAME.isin(similiar_name)]

    def memory_rule(self, name1=None, name2=None, name3=None, form_drug=None):
        if name1 is None:
            name1 = 'NA'
        if name2 is None:
            name2 = 'NA'
        if name3 is None:
            name3 = 'NA'
        if form_drug is None:
            form_drug = 'NA'
        print(name1, name2, name3, form_drug)
        return self.memory_dict[(self.memory_dict.PRODUCT_NAME == name1) & \
                                (self.memory_dict.GENERIC_NAME == name2) & \
                                (self.memory_dict.TRAD_NAME == name3) & \
                                (self.memory_dict.DRUG_FORM == form_drug)]

    def similiar_rule(self, name1=None, name2=None, name3=None, form_drug=None):
        product_name = []
        for single_name in self.df_raw.PRODUCT_NAME:
            ratio = (len(name1) + len(single_name)) / len(set(name1 + single_name))
            if ratio > 1.75:
                product_name.append(single_name)
        return self.df_raw[self.df_raw.PRODUCT_NAME.isin(product_name)]

    def bat_process(self, n1=None, n2=None, n3=None, drug=None):
        if n1 != None:
            n1 = n1.replace('（', '(')
            n1 = n1.replace('）', ')')
            n1 = re.sub('[\s\-]', '', n1)
        data_result = self.full_match_l1(name1=n1, name2=n2, name3=n3, form_drug=drug)
        if data_result.shape[0] > 0:
            final_result = data_result
            final_result['rule'] = 'full_match_l1'
            final_result['type'] = '|'
        elif self.rule_1(name1=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:
            final_result = self.rule_1(name1=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'rule_1'
            final_result['type'] = '|'
        elif self.rule_2(name1=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:
            final_result = self.rule_2(name1=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'rule_2'
            final_result['type'] = '|'
        elif self.rule_5(name=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:
            final_result = self.rule_5(name=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'rule_5'
            final_result['type'] = '|'
        elif self.rule_4(name1=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:
            final_result = self.rule_4(name1=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'rule_4'
            final_result['type'] = '|'
        elif self.rule_11(name1=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:

            final_result = self.rule_11(name1=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'rule_11'
            final_result['type'] = '|'

        elif self.rule_12(name1=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:
            final_result = self.rule_12(name1=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'rule_12'
            final_result['type'] = '|'

        elif self.memory_rule(name1=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:
            final_result = self.memory_rule(name1=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'memory_rule'
            final_result['type'] = 'memory_rule'

        elif self.full_match_l2(name1=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:
            final_result = self.full_match_l2(name1=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'full_match_l2'
            final_result['type'] = '||'

        elif self.full_match_l3(name1=n1, name2=n2, name3=n3).shape[0] > 0:
            final_result = self.full_match_l3(name1=n1, name2=n2, name3=n3)
            final_result['rule'] = 'full_match_l3'
            final_result['type'] = '|||'
        ###三级   
        elif self.rule_8(name1=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:
            final_result = self.rule_8(name1=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'rule_8'
            final_result['type'] = '|||'
        elif self.rule_3(name1=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:
            final_result = self.rule_3(name1=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'rule_3'
            final_result['type'] = '|||'

        elif self.rule_6(name1=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:
            final_result = self.rule_6(name1=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'rule_6'
            final_result['type'] = '|||'
        elif self.similiar_rule(name1=n1, name2=n2, name3=n3, form_drug=drug).shape[0] > 0:
            final_result = self.similiar_rule(name1=n1, name2=n2, name3=n3, form_drug=drug)
            final_result['rule'] = 'similiar_rule'
            final_result['type'] = 'similiar_rule'
        else:
            final_result = self.df_raw[self.df_raw.PRODUCT_NAME == 'test']
            final_result['rule'] = 'None'
            final_result['type'] = 'None'
        # final_result=final_result.duplicated()
        final_result = final_result[['LEVEL1', 'LEVEL2', 'LEVEL3', 'PRODUCT_NAME', 'rule', 'type']]
        return final_result.to_json(force_ascii=False, orient='index')

        # def return:
        #    a.to_json(force_ascii=False,orient='index')
