
with user_info as (
select
    channel_group_id,  -- 渠道组id
    channel_group_name,  -- 渠道组名称
    channel_id,  -- 子渠道id
    enroll_channel_type,  -- 招生渠道类型
    renewal_channel_type,  -- 续报渠道类型
    channel_subtype_name,  -- 市场后台渠道子类型
    budget_group_name,  -- 业务核算组
    concat(term_year,term_season) as season,
    concat(term_year,term_name_type) as term,
    operation_type_name,
    parent_operation_type_name,
    term_start_time,  --学期开始时间
    user_id,
    parents_city_level,
    is_inrenewal_period,  -- 是否当期续报
    renewal_user_cnt  -- 续报人数
from
    (
    select *,row_number() over(partition by term_id,user_id order by user_class_start_time desc ) as rk
    from htcdm.dws_l1_order_term_learning_renewal_hdf
    where dt = regexp_replace(date_sub(current_date(),1),'-','')
        and substr(pay_time,1,10) between date_sub(current_date(),180) and date_sub(current_date(),0)
        and parent_operation_type_name in ('9.9','0元')
        and enroll_channel_type not in ('转介绍','线下地推','自然量','创新玩具产品部','内部扩科')
        and order_status != 'UNPAID'
    )c
where c.rk = 1
)
select
    inf.renewal_channel_type as `续报渠道类型`,
    inf.channel_subtype_name as `市场后台渠道子类型`,
    inf.budget_group_name as `业务核算组`,
    inf.season as `学季`,
    inf.term `学期期次`,
    concat(inf.parent_operation_type_name,'-',inf.renewal_channel_type,'-',inf.channel_subtype_name,'-',inf.enroll_channel_type),
    inf.operation_type_name as `学期类型`,
    inf.parent_operation_type_name as `业务线`,
    case when inf.parents_city_level = '一线' then 1
         when inf.parents_city_level = '新一线' then 2
         when inf.parents_city_level = '二线' then 3
         when inf.parents_city_level = '三线' then 4
         when inf.parents_city_level = '四线' then 5
         when inf.parents_city_level = '五线' then 6
         else null end as city_level_order,
    case when substr(inf.season,5,1) = '寒' then 1
         when substr(inf.season,5,1) = '春' then 2
         when substr(inf.season,5,1) = '暑' then 3
         when substr(inf.season,5,1) = '秋' then 4 else null end as season_order,
    inf.parents_city_level as `城市等级`,
    count(distinct inf.user_id) as `招生量`,
    count(distinct if(is_inrenewal_period = 1,inf.user_id,null)) as `续报数`,
    count(distinct if(is_inrenewal_period = 1,inf.user_id,null)) /count(distinct inf.user_id) as `续报率`
    -- coalesce(sum(if(is_inrenewal_period = 1, renewal_user_cnt,0)),0) as `续报数`,
    -- concat(round(coalesce(sum(if(is_inrenewal_period = 1, renewal_user_cnt,0)),0)*100/count(distinct inf.user_id),2),'%') as `续报率`
from user_info inf
where
    channel_group_id is not null
    and inf.operation_type_name != '0元课新兵营'
    and concat(inf.parent_operation_type_name,'-',inf.renewal_channel_type,'-',inf.channel_subtype_name,'-',inf.enroll_channel_type) in ('9.9-短信-短信-CPA',
'9.9-进校合作-其它-进校-春辉',
'9.9-进校合作-其它-进校-崔白',
'9.9-线上BD商务-TMK-链接-CPA',
'9.9-线上BD商务-其它-CPA',
'9.9-召回-老用户召回-CPA',
'9.9-直播-kol-抖音-CPA',
'9.9-直播-kol-抖音-其它',
'9.9-直播-kol-抖音-数字化营销',
'9.9-直播-kol-视频号-CPA',
'9.9-直播-kol-视频号-数字化营销',
'9.9-直播投流-千川-自营直播-数字化营销',
'9.9-直播投流-视频号-自营直播-CPA',
'9.9-直播投流-视频号-自营直播-数字化营销',
'0元-BtoC-其它-BtoC',
'0元-短信-短信-CPA',
'0元-进校合作-其它-进校-春辉',
'0元-进校合作-其它-进校-崔白',
'0元-线上BD商务-TMK-表单-CPA',
'0元-线上BD商务-TMK-表单-其它',
'0元-线上BD商务-TMK-链接-CPA'
'0元-线上BD商务-公众号-CPA',
'0元-线上BD商务-其它-CPA',
'0元-线上BD商务-社群运营-CPA',
'0元-线上BD商务-淘宝-CPA',
'0元-线上BD商务-中小长尾媒体-CPA',
'0元-召回-老用户召回-CPA',
'0元-直播-kol-抖音-CPA',
'0元-直播-kol-抖音-数字化营销',
'0元-直播-kol-视频号-CPA')
group by
    inf.renewal_channel_type,
    inf.channel_subtype_name,
    inf.budget_group_name,
    inf.season,
    inf.term,
    inf.operation_type_name,
    inf.parent_operation_type_name,
    inf.parents_city_level,
    concat(inf.parent_operation_type_name,'-',inf.renewal_channel_type,'-',inf.channel_subtype_name,'-',inf.enroll_channel_type)
order by
    city_level_order,season_order,inf.term
