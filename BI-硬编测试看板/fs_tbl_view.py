import pandas as pd

def dat_pre(cost, raw):
    """数据预处理"""
    cost_df = pd.DataFrame(cost)
    raw_df = pd.DataFrame(raw)
    raw_df = raw_df.drop_duplicates(subset=['user_id'])
    cost_df['渠道组id'] = cost_df['渠道组id'].astype(str)
    raw_df['channel_group_id'] = raw_df['channel_group_id'].astype(str)
    raw_df['child_age'].fillna('0', inplace=True)
    raw_df['child_age'] = raw_df['child_age'].astype(int)
    raw_df['is_renewal'] = raw_df['is_renewal'].astype(int)
    raw_df['login_os'].fillna('未知', inplace=True)
    cost_df['成本金额'] = pd.to_numeric(cost_df['成本金额'], errors='coerce')
    merged_df = pd.merge(cost_df, raw_df, how='left', left_on='渠道组id', right_on='channel_group_id')
    # 转换日期字段的类型
    merged_df['pay_time'] = pd.to_datetime(merged_df['pay_time']).dt.date
    merged_df['开始日期'] = pd.to_datetime(merged_df['开始日期']).dt.date
    merged_df['结束日期'] = pd.to_datetime(merged_df['结束日期']).dt.date
    # 过滤出满足时间条件的数据
    merged_df = merged_df[
        (merged_df['pay_time'] >= merged_df['开始日期']) & (merged_df['pay_time'] <= merged_df['结束日期'])]

    # 计算 CAC（成本金额 / 用户数量）
    merged_df['cac'] = merged_df.groupby(['渠道组id', '开始日期', '结束日期'])['成本金额'].transform('mean') / \
                       merged_df.groupby(['渠道组id', '开始日期', '结束日期'])['user_id'].transform('count')

    # 创建结果 DataFrame
    result_df = pd.merge(raw_df, merged_df[['user_id', 'cac', '开始日期', '结束日期']], how='left', on='user_id')
    return result_df
def enroll_total(dat):
    """raw-招生数据-汇总"""
    # 累计招生总量
    total_enrollment = dat['user_id'].nunique()
    # 有成本招生 L1CAC
    l1cac = dat['cac'].dropna().mean()
    # 有成本招生量
    enrollment_with_cost = len(set(dat.loc[dat['cac'].notna(), 'user_id']))
    # 累计招生总量和续报数
    #renewal_data = dat[dat['is_renewal_end'] == 1]
    renewal_data = dat
    total_renewal_count = renewal_data['is_renewal'].sum()
    total_renewal_enrollment = len(set(renewal_data['user_id']))
    # 已结束续报累计续报率
    total_renewal_rate = total_renewal_count / total_renewal_enrollment if total_renewal_enrollment > 0 else 0

    result_df_1 = pd.DataFrame({
        '累计招生总量': [total_enrollment],
        '有成本招生量': [enrollment_with_cost],
        '有成本招生L1CAC': [l1cac],
        '累计续报率': [total_renewal_rate]
    })

    return result_df_1

def enroll_term(dat):
    """raw-招生数据-学期"""
    result_df = pd.DataFrame()

    # 按学期分组
    for term, group_data in dat.groupby('term_name_type'):
        total_enrollment = group_data['user_id'].nunique()

        enrollment_with_cost = group_data.loc[group_data['cac'].notna(), 'user_id'].nunique()
        l1cac = round(group_data['cac'].dropna().mean(), 2) if enrollment_with_cost > 0 else 0
        enrollment_without_cost = total_enrollment - enrollment_with_cost
        # 已结束续报的累计招生总量和续报数
        # renewal_data = group_data[group_data['is_renewal_end'] == 1]
        renewal_data = group_data
        total_renewal_count = renewal_data['is_renewal'].sum()
        total_renewal_enrollment = renewal_data['user_id'].nunique()

        # 已结束续报累计续报率
        total_renewal_rate = (total_renewal_count / total_renewal_enrollment) if total_renewal_enrollment > 0 else 0

        temp_df = pd.DataFrame({
            '学期': [term],
            '已录成本招生量': [enrollment_with_cost],
            '未录成本招生量': [enrollment_without_cost],
            'L1CAC': [l1cac],
            '续报率': [total_renewal_rate]
        })
        temp_df['续报率'] = temp_df['续报率'].astype('float64')
        result_df = pd.concat([result_df, temp_df], ignore_index=True)
    return result_df

def enroll_term_channel(dat):
    """raw-招生数据-学期&渠道"""
    result_df = pd.DataFrame()
    for (term, channel), group_data in dat.groupby(['term_name_type', 'channel_subtype_name']):
        l1cac = round(group_data['cac'].dropna().mean(), 2) if not group_data['cac'].dropna().empty else None
        enrollment_with_cost = group_data.loc[group_data['cac'].notna(), 'user_id'].nunique()
        #renewal_data = group_data[group_data['is_renewal_end'] == 1]
        renewal_data = group_data
        total_renewal_count = renewal_data['is_renewal'].sum()
        total_renewal_enrollment = renewal_data['user_id'].nunique()
        total_renewal_rate = total_renewal_count / total_renewal_enrollment if total_renewal_enrollment > 0 else 0

        temp_df = pd.DataFrame({
            '学期': [term],
            '渠道': [channel],
            '招生量': [enrollment_with_cost],
            'L1CAC': [l1cac],
            '续报率': [total_renewal_rate]
        })
        temp_df = temp_df[temp_df['L1CAC'].notna()]
        result_df = pd.concat([result_df, temp_df], ignore_index=True)

    return result_df
def funnel_term(dat,raw_soft):
    """raw-过程数据-学期"""
    result_df = pd.DataFrame()
    dat['类型'] = '硬编'
    raw_soft['类型'] = '软编'
    #去除8月23日之后进其他学期的订单
    raw_soft = raw_soft[~raw_soft['term_name_type'].isin(["暑09期", "秋01期"])]
    combined_data = pd.concat([dat, raw_soft], ignore_index=True)
    for (term, course_type), group_data in combined_data.groupby(
            ['term_name_type', '类型']):
        enrollment_count = group_data['user_id'].nunique()
        login_rate = group_data['is_login'].sum() / enrollment_count
        add_wx_rate = group_data['is_add_wx'].sum() / enrollment_count
        att_u1_rate = group_data['att_u1'].sum() / enrollment_count
        fns_last_unit_rate = group_data['fns_last_unit'].sum() / enrollment_count
        retention_rate = float(group_data['fns_last_unit'].sum()) / float(group_data['att_u1'].sum()) if group_data['att_u1'].sum() > 0 else 0

        complete_trans_rate = float(group_data['is_renewal'].sum())/float(group_data['fns_last_unit'].sum()) if group_data['fns_last_unit'].sum() > 0 else 0
        renewal_rate = float(group_data['is_renewal'].sum()) / enrollment_count

        temp_df = pd.DataFrame({
            '学期': [term],
            '类型': [course_type],
            '招生量': [enrollment_count],
            '登录率': [login_rate],
            '加微率': [add_wx_rate],
            '首到率': [att_u1_rate],
            '完课率': [fns_last_unit_rate],
            '留存率': [retention_rate],
            '完转率': [complete_trans_rate],
            '续报率': [renewal_rate]
        })
        for rate_col in ['登录率', '加微率', '首到率', '完课率', '留存率', '完转率', '续报率']:
            temp_df[rate_col] = temp_df[rate_col].astype('float64')

        result_df = pd.concat([result_df, temp_df], ignore_index=True)
        result_df.reset_index(drop=True, inplace=True)
    return result_df

# ...

def funnel_term_gender(dat):
    """raw-过程数据-学期&性别"""
    ## 按学期和家长性别分组
    # 字段：
    ## 招生量 unique user_id
    ## 登录率： （is_login == 1）人数/招生量
    ## 加微率： （is_add_wx == 1）人数/招生量
    ## 首到率： （att_u1 == 1）人数/招生量
    ## 完课率： （fns_last_unit == 1）人数/招生量
    ## 留存率： （fns_last_unit == 1）人数/（att_u1 == 1）人数
    ## 完转率： （is_renewal == 1）/（fns_last_unit == 1 ）人数
    ## 续报率： （is_renewal == 1）人数/招生量
    result_df = pd.DataFrame()

    for (term, gender), group_data in dat.groupby(['term_name_type', 'parents_gender']):
        enrollment_count = group_data['user_id'].nunique()
        login_rate = group_data['is_login'].sum() / enrollment_count
        add_wx_rate = group_data['is_add_wx'].sum() / enrollment_count
        att_u1_rate = group_data['att_u1'].sum() / enrollment_count
        fns_last_unit_rate = group_data['fns_last_unit'].sum() / enrollment_count
        retention_rate = group_data['fns_last_unit'].sum() / group_data['att_u1'].sum() if group_data[
                                                                                               'att_u1'].sum() > 0 else 0
        complete_trans_rate = float(group_data['is_renewal'].sum()) / float(group_data['fns_last_unit'].sum()) if group_data['fns_last_unit'].sum() > 0 else 0 if group_data['fns_last_unit'].sum() > 0 else 0
        renewal_rate = group_data['is_renewal'].sum() / enrollment_count

        temp_df = pd.DataFrame({
            '学期': [term],
            '家长性别': [gender],
            '招生量': [enrollment_count],
            '登录率': [login_rate],
            '加微率': [add_wx_rate],
            '首到率': [att_u1_rate],
            '完课率': [fns_last_unit_rate],
            '留存率': [retention_rate],
            '完转率': [complete_trans_rate],
            '续报率': [renewal_rate]
        })

        # Ensure the rates are of type float64
        for rate_col in ['登录率', '加微率', '首到率', '完课率', '留存率', '完转率', '续报率']:
            temp_df[rate_col] = temp_df[rate_col].astype('float64')

        result_df = pd.concat([result_df, temp_df], ignore_index=True)

    return result_df


def hard_soft_contrast(dat,raw_soft):
    """raw-过程数据-学期&千川"""
    result_df = pd.DataFrame()
    dat['类型'] = '硬编'
    raw_soft['类型'] = '软编'
    raw_soft = raw_soft[~raw_soft['term_name_type'].isin(["暑09期", "秋01期"])]
    combined_data = pd.concat([dat, raw_soft], ignore_index=True)
    for (term, course_type, city_level), group_data in combined_data.groupby(
            ['term_name_type', '类型', 'parents_city_level']):
        enrollment_count = group_data['user_id'].nunique()
        login_rate = group_data['is_login'].sum() / enrollment_count
        add_wx_rate = group_data['is_add_wx'].sum() / enrollment_count
        att_u1_rate = group_data['att_u1'].sum() / enrollment_count
        fns_last_unit_rate = group_data['fns_last_unit'].sum() / enrollment_count
        retention_rate = float(group_data['fns_last_unit'].sum()) / float(group_data['att_u1'].sum()) if group_data['att_u1'].sum() > 0 else 0
        complete_trans_rate = float(group_data['is_renewal'].sum())/float(group_data['fns_last_unit'].sum()) if group_data['fns_last_unit'].sum() > 0 else 0
        renewal_rate = float(group_data['is_renewal'].sum()) / enrollment_count

        temp_df = pd.DataFrame({
            '学期': [term],
            '类型': [course_type],
            '城市等级': [city_level],
            '招生量': [enrollment_count],
            '登录率': [login_rate],
            '加微率': [add_wx_rate],
            '首到率': [att_u1_rate],
            '完课率': [fns_last_unit_rate],
            '留存率': [retention_rate],
            '完转率': [complete_trans_rate],
            '续报率': [renewal_rate]
        })
        for rate_col in ['登录率', '加微率', '首到率', '完课率', '留存率', '完转率', '续报率']:
            temp_df[rate_col] = temp_df[rate_col].astype('float64')

        result_df = pd.concat([result_df, temp_df], ignore_index=True)
        city_level_order = ['一线','新一线', '二线', '三线', '四线', '五线']
        result_df['城市等级'] = pd.Categorical(result_df['城市等级'], categories=city_level_order, ordered=True)
        result_df.sort_values(['学期', '类型', '城市等级'], inplace=True)
        result_df.reset_index(drop=True, inplace=True)
    return result_df


def funnel_term_age(dat):
    """raw-过程数据-年龄"""
    result_df = pd.DataFrame()

    for (term, age), group_data in dat.groupby(['term_name_type', 'child_age']):
        enrollment_count = group_data['user_id'].nunique()
        login_rate = group_data['is_login'].sum() / enrollment_count
        add_wx_rate = group_data['is_add_wx'].sum() / enrollment_count
        att_u1_rate = group_data['att_u1'].sum() / enrollment_count
        fns_last_unit_rate = group_data['fns_last_unit'].sum() / enrollment_count
        retention_rate = group_data['fns_last_unit'].sum() / group_data['att_u1'].sum() if group_data[
                                                                                               'att_u1'].sum() > 0 else 0
        complete_trans_rate = float(group_data['is_renewal'].sum()) / float(group_data['fns_last_unit'].sum()) if \
        group_data['fns_last_unit'].sum() > 0 else 0 if group_data['fns_last_unit'].sum() > 0 else 0
        renewal_rate = group_data['is_renewal'].sum() / enrollment_count

        temp_df = pd.DataFrame({
            '学期': [term],
            '学生年龄': [age],
            '招生量': [enrollment_count],
            '登录率': [login_rate],
            '加微率': [add_wx_rate],
            '首到率': [att_u1_rate],
            '完课率': [fns_last_unit_rate],
            '留存率': [retention_rate],
            '完转率': [complete_trans_rate],
            '续报率': [renewal_rate]
        })

        # Ensure the rates are of type float64
        for rate_col in ['登录率', '加微率', '首到率', '完课率', '留存率', '完转率', '续报率']:
            temp_df[rate_col] = temp_df[rate_col].astype('float64')

        result_df = pd.concat([result_df, temp_df], ignore_index=True)

    return result_df


def funnel_term_os(dat):
    """raw-过程数据-登录设备"""
    result_df = pd.DataFrame()

    for (term, os), group_data in dat.groupby(['term_name_type', 'login_os']):
        enrollment_count = group_data['user_id'].nunique()
        login_rate = group_data['is_login'].sum() / enrollment_count
        add_wx_rate = group_data['is_add_wx'].sum() / enrollment_count
        att_u1_rate = group_data['att_u1'].sum() / enrollment_count
        fns_last_unit_rate = group_data['fns_last_unit'].sum() / enrollment_count
        retention_rate = group_data['fns_last_unit'].sum() / group_data['att_u1'].sum() if group_data[
                                                                                               'att_u1'].sum() > 0 else 0
        complete_trans_rate = float(group_data['is_renewal'].sum()) / float(group_data['fns_last_unit'].sum()) if \
        group_data['fns_last_unit'].sum() > 0 else 0 if group_data['fns_last_unit'].sum() > 0 else 0
        renewal_rate = group_data['is_renewal'].sum() / enrollment_count

        temp_df = pd.DataFrame({
            '学期': [term],
            '登录设备': [os],
            '招生量': [enrollment_count],
            '登录率': [login_rate],
            '加微率': [add_wx_rate],
            '首到率': [att_u1_rate],
            '完课率': [fns_last_unit_rate],
            '留存率': [retention_rate],
            '完转率': [complete_trans_rate],
            '续报率': [renewal_rate]
        })

        # Ensure the rates are of type float64
        for rate_col in ['登录率', '加微率', '首到率', '完课率', '留存率', '完转率', '续报率']:
            temp_df[rate_col] = temp_df[rate_col].astype('float64')

        result_df = pd.concat([result_df, temp_df], ignore_index=True)

    return result_df