#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
from python.work.crawler import wiki8
from python.work.crawler import cnki

IP = '192.168.5.94'

# 中西药--------------------------------------------------------------------------------
# cfda(ip='192.168.5.94')

# 中药以及中药方剂-----------------------------------------------------------------------
# zhongyaofangji(ip='192.168.5.94')
# yaozh_zyfj(ip='192.168.5.94')
# yaozh_zy(ip='192.168.5.94')

# 药品----------------------------------------------------------------------------------
# yaozh_interaction(ip='192.168.16.113') # 相互作用
# yaozh_monitored('192.168.5.94') # 辅助与重点监控用药
# yaozh_unlabeleduse('192.168.5.94') # 超说明书

# 疾病----------------------------------------------------------------------------------
# cnki.disease_pmmp('192.168.5.94')
# cnki.disease_lczl(IP).to_excel() # 完成 v1.1
# wiki8.disease('192.168.5.94')  #  完成 v1.1
# rw.disease('192.168.5.94')  # v1.1
# medlive.disease('192.168.5.94')

# 手术----------------------------------------------------------------------------------
# cnki.operation_pmmp(IP).to_excel() # 完成 v1.1
# cnki.operation_lczl(IP).to_excel()  # 完成 v1.1
# wiki8.operation(IP).to_excel()  # 完成 v1.1

# 检查----------------------------------------------------------------------------------
# cnki.diagnostic_examination(IP).to_excel()  # 完成 v1.1
# cnki.auxiliary_examination_lczl(IP).to_excel()  # 完成 v1.1

if __name__ == '__main__':
    wiki8.disease(IP).to_excel()
