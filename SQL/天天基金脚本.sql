-- # 历史净值表 Net value of history
-- # Net Asset Value（NAV）单位净值
-- # Cumulative net 累积净值
-- # growth rate 增长率
-- # redemption 赎回
-- # subscribe 申购
-- # 基金  fund
-- # FUND_CODE 基金代码
-- # service charge 手续费
-- #  purchase 购买
CREATE TABLE FUND_NET_VALUE_HISTORY (
  FUND_CODE  VARCHAR2(6),
  FUND_DATE  VARCHAR2(255),
  NAV        VARCHAR2(255),
  NC         VARCHAR2(255),
  GROWTHRATE VARCHAR2(255),
  SUBSCRIBE  VARCHAR2(255),
  REDEMPTION VARCHAR2(255)
);
ALTER TABLE FUND_NET_VALUE_HISTORY
  ADD (CREATE_TIME DATE DEFAULT SYSDATE);

SELECT *
FROM (SELECT
        FUND_CODE,
        COUNT(FUND_CODE)
      FROM FUND_NET_VALUE_HISTORY
      GROUP BY FUND_CODE)
WHERE FUND_CODE IN ('340008', '161725', '070032', '110022', '000457');
SELECT *
FROM FUND_NET_VALUE_HISTORY
WHERE TO_DATE(FUND_DATE, 'YYYY-MM-DD') >= TO_DATE('2018-01-02', 'YYYY-MM-DD')
      AND FUND_CODE IN ('340008', '161725', '070032', '110022', '000457');

-- 每日开方式基金净值表
DROP TABLE FUND_OPENFUNDNETVALUE;
CREATE TABLE FUND_OPENFUNDNETVALUE
(
  FUND_CODE      VARCHAR2(6) PRIMARY KEY NOT NULL,
  FUND_NAME      VARCHAR2(255),
  FUND_NAME_PY   VARCHAR2(25),
  REDEMPTION     VARCHAR2(25),
  SUBSCRIBE      VARCHAR2(25),
  SERVICE_CHARGE VARCHAR2(25),
  PURCHASE_STATR VARCHAR2(2)
);
CREATE UNIQUE INDEX FUND_OPENFUNDNETVALUE_FUND_CODE_uindex
  ON FUND_OPENFUNDNETVALUE (FUND_CODE);
INSERT INTO FUND_OPENFUNDNETVALUE (FUND_CODE, FUND_NAME, FUND_NAME_PY, REDEMPTION, SUBSCRIBE, SERVICE_CHARGE, PURCHASE_STATR)
VALUES (:1, :2, :3, :4, :5, :6, :7)

SELECT FUND_NAME
FROM FUND_OPENFUNDNETVALUE
WHERE FUND_CODE = :fundCode;
SELECT *
FROM FUND_OPENFUNDNETVALUE;

-- 基金概况表
CREATE TABLE FUND_GENERAL_SITUATION (
  FUND_CODE              VARCHAR2(6) NOT NULL PRIMARY KEY,
  FULL_NAME              VARCHAR2(255),
  SHORTCUT_NAME          VARCHAR2(255),
  FUND_TYPE              VARCHAR2(255),
  ISSUING_DATE           VARCHAR2(255),
  DATE_AND_SCALE         VARCHAR2(255), -- 发行日期/规模
  ASSET_SIZE             VARCHAR2(255), -- 资产规模
  SHARE_SIZE             VARCHAR2(255), -- 份额规模
  CUSTODIAN              VARCHAR2(255), -- 管理人
  TRUSTEE                VARCHAR2(255), -- 托管人
  HANDLER                VARCHAR2(255), -- 经理人
  PARTICIPATION_PROFIT   VARCHAR2(255), -- 成立分红
  MANAGE_CHARGE          VARCHAR2(255), -- 管理费率
  TRUSTEE_CHARGE         VARCHAR2(255), -- 托管费率
  SELL_SERVICE_CHARGE    VARCHAR2(255), -- 销售服务费率
  HIGH_SUBSCRIBE         VARCHAR2(255), -- 认购
  HIGH_REDEMPTION        VARCHAR2(255), -- 赎回
  HIGH_SUBSCRIBE2        VARCHAR2(255), -- 申购
  PERFORMANCE_EVALUATION VARCHAR2(255), -- 业绩
  TAIL_AFTER             VARCHAR2(255), -- 跟踪
  OTHER                  CLOB
);
INSERT INTO FUND_GENERAL_SITUATION (FUND_CODE, FULL_NAME, SHORTCUT_NAME, FUND_TYPE, ISSUING_DATE, DATE_AND_SCALE, ASSET_SIZE, SHARE_SIZE, CUSTODIAN, TRUSTEE, HANDLER, PARTICIPATION_PROFIT, MANAGE_CHARGE, TRUSTEE_CHARGE, SELL_SERVICE_CHARGE, HIGH_SUBSCRIBE, HIGH_REDEMPTION, HIGH_SUBSCRIBE2, PERFORMANCE_EVALUATION, TAIL_AFTER, OTHER)
VALUES
  (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21)

SELECT
  GROWTHRATE,
  NAV
FROM FUND_NET_VALUE_HISTORY
WHERE FUND_CODE = '340008'
      AND TO_DATE(FUND_DATE, 'yyyy-MM-dd') > TO_DATE('2017-12-01', 'yyyy-MM-dd')
-- AND TO_DATE(FUND_DATE, 'yyyy-MM-dd') < TO_DATE('2014-05-31', 'yyyy-MM-dd')
ORDER BY FUND_DATE;

SELECT *
FROM FUND_OPENFUNDNETVALUE
WHERE FUND_CODE NOT IN (SELECT FUND_CODE
                        FROM FUND_NET_VALUE_HISTORY
                        GROUP BY FUND_CODE);
