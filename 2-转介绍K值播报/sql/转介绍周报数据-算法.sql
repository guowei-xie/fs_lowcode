with user_base as (
  select
    term_id,
    term_name,
    user_class_group_id,
    user_id,
    min(user_class_start_time) as user_class_start_time,
    max(user_class_end_time) as user_class_end_time
  from
    htcdm.dws_consum_perform_acc_hdf
  where
    dt = regexp_replace(date_sub(current_date(), 1), '-', '')
    and user_class_status = 1
    and user_id > 0
    and term_ids in ?term_ids
  group by
    term_id,
    term_name,
    user_class_group_id,
    user_id
),
dim_date as (
  select
    date(date_str) as monday_of_week
  from
    htcdm.dim_pub_date
  where
    day_of_week = 1
    and date(date_str) >= '2020-01-01'
    and date(date_str) <= current_date()
),
referral_info as
(
select user_id,
        term_id,
        monday_of_week,
        is_enter,
        is_save,
        is_upload,
        is_att,
        touch_cnt,
        invite_l1_cnt,
        invite_annual_cnt
from app.app_tutor_referral_user_invite_df  --新数仓未覆盖
where dt = regexp_replace(date_sub(current_date(), 1), '-', '')
)
,
browser as -- 用户转介绍活动浏览
(
  select
    distinct user_id,
    case
      when dayofweek(date(event_time)) = 1 then date_sub(date(event_time), 6)
      else date_sub(date(event_time), dayofweek(date(event_time)) -2)
    end as monday_of_week
  from
    gdm.gdm_ua_event_referral_entrance_df
  where
    dt = regexp_replace(date_sub(current_date(), 1), '-', '')
    and referral_activity_type = '转介绍'
    and user_id > 0
),
poster_save as -- 下载海报
(
  select
    distinct user_id,
    case
      when dayofweek(date(event_time)) = 1 then date_sub(date(event_time), 6)
      else date_sub(date(event_time), dayofweek(date(event_time)) -2)
    end as monday_of_week
  from
    gdm.gdm_ua_event_referral_poster_df
  where
    dt = regexp_replace(date_sub(current_date(), 1), '-', '')
    and bridge_id is not null
    and user_id > 0
),
invite_result_tmp as (
  select
    user_id,
    inviter_id,
    order_no
  from
    htcdm.dws_trade_order_stat_hdf
  where
    dt = regexp_replace(date_sub(current_date(), 1), '-', '')
    and package_group = 1
    and inviter_id > 0
    and user_id > 0
),
is_renew as (
      select
        order_no as source_order_number,
        max(l1_channel_renewal_order_no) as apply_order_number
      from
        htcdm.dws_trade_renewal_l1_channel_hdf
      where
        dt = date_format(date_sub(current_date(), 1), 'yyyyMMdd')
        and l1_channel_renewal_order_status <> 'UNPAID'
        and l1_channel_renewal_order_status is not null
        and l1_channel_renewal_course_type = 'ANNUAL'
        and l1_channel_renewal_package_course_type <> 'Math'
      group by
        order_no
),
invite_pub_tmp as (
  select
    user_id as referral_inviter_id,
    invite_time,
    is_valid_invite as is_invite_succeed,
    acceptor_id as referral_acceptor_id
  from htcdm.dwd_mkt_referral_invite_hdf
    --gdm.gdm_ua_event_referral_relation_df --新数仓无该表
  where
    dt = regexp_replace(date_sub(current_date(), 1), '-', '')
--     and land_page_ip not in (
--       '61.151.178.150',
--       '61.129.11.211',
--       '113.96.221.178',
--       '113.96.223.240',
--       '113.96.219.105',
--       '58.251.98.105',
--       '61.151.202.84',
--       '113.96.223.239',
--       '58.251.98.100',
--       '113.96.223.176'
--     )
),
invite_tmp as (
  select
    referral_inviter_id as user_id,
    invite_time,
    is_invite_succeed,
    referral_acceptor_id,
    case
      when is_renew.source_order_number is not null then 1
    end as is_renew
  from
    invite_pub_tmp
    left join invite_result_tmp on invite_pub_tmp.referral_acceptor_id = invite_result_tmp.user_id
    and invite_pub_tmp.referral_inviter_id = invite_result_tmp.inviter_id
    left join is_renew on is_renew.source_order_number = invite_result_tmp.order_no
),
invite_pub as (
  select
    invite_tmp.user_id,
    case
      when dayofweek(date(invite_time)) = 1 then date_sub(date(invite_time), 6)
      else date_sub(
        date(invite_time),
        dayofweek(date(invite_time)) -2
      )
    end as monday_of_week,
    count(distinct referral_acceptor_id) as reach,
    count(
      distinct case
        when is_invite_succeed = 1 then referral_acceptor_id
      end
    ) as succeed_l1,
    sum(invite_tmp.is_renew) as succeed_l2
  from
    user_base
    left join invite_tmp on invite_tmp.user_id = user_base.user_id
  group by
    invite_tmp.user_id,
    case
      when dayofweek(date(invite_time)) = 1 then date_sub(date(invite_time), 6)
      else date_sub(
        date(invite_time),
        dayofweek(date(invite_time)) -2
      )
    end
),
class_attend as (
  select
    term_id,
    case
      when dayofweek(date(unit_unlocked_time)) = 1 then date_sub(date(unit_unlocked_time), 6)
      else date_sub(
        date(unit_unlocked_time),
        dayofweek(date(unit_unlocked_time)) -2
      )
    end as monday_of_week,
    count(distinct user_id) as user_attend_cnt
  from
    htcdm.dws_consum_user_learning_progress_hdf
  where
    dt = regexp_replace(current_date(), '-', '')
    and term_id > 0
    and term_ids in ?term_ids
  group by
    term_id,
    case
      when dayofweek(date(unit_unlocked_time)) = 1 then date_sub(date(unit_unlocked_time), 6)
      else date_sub(
        date(unit_unlocked_time),
        dayofweek(date(unit_unlocked_time)) -2
      )
    end
),
user_attend_cnt as (
  select
    term_id,
    monday_of_week,
    user_attend_cnt,
    dense_rank () over (
      partition by term_id
      order by
        monday_of_week
    ) as tempo
  from
    class_attend
),
referral_data_tmp as
(
select
	user_base.term_id,
    user_base.term_name,
    user_base.user_id,
    date(referral_info.monday_of_week) as monday_of_week,
    referral_info.is_enter,
    referral_info.is_save,
    referral_info.is_upload,
    referral_info.is_att,
    referral_info.touch_cnt,
    referral_info.invite_l1_cnt,
    referral_info.invite_annual_cnt
from user_base
left join referral_info on user_base.term_id = referral_info.term_id
and user_base.user_id = referral_info.user_id
)
,
referral_data as (
  select
    user_base.term_id,
    user_base.term_name,
    dim_date.monday_of_week,
    count(distinct user_base.user_id) as `user_cnt`,
    count(distinct case when is_enter = 1 then user_base.user_id end) as `browser_cnt`,
    count(distinct case when is_save = 1 then user_base.user_id end) as `poster_cnt`,
    count(distinct case when is_att = 1 then user_base.user_id end) as `att_cnt`,
    count(distinct case when is_upload = 1 then user_base.user_id end) as `upload_cnt`,
    sum(referral_data_tmp.touch_cnt) as `reach`,
    sum(referral_data_tmp.invite_l1_cnt) as `succeed_l1`,
    sum(referral_data_tmp.invite_annual_cnt) as `succeed_l2`
  from
  	user_base
  left join dim_date on 1 = 1
  left join referral_data_tmp on user_base.user_id = referral_data_tmp.user_id
  and dim_date.monday_of_week = referral_data_tmp.monday_of_week
  group by
    user_base.term_id,
    user_base.term_name,
    dim_date.monday_of_week
)
,
referral_week_data as (
  select
    referral_data.term_id,
    referral_data.term_name,
    referral_data.monday_of_week,
    referral_data.user_cnt,
    referral_data.browser_cnt,
    referral_data.poster_cnt,
    referral_data.upload_cnt,
    referral_data.att_cnt,
    referral_data.reach,
    sum(referral_data.reach) over (
      partition by referral_data.term_id
      order by
        referral_data.monday_of_week asc
    ) as cum_reach,
    referral_data.succeed_l1,
    sum(referral_data.succeed_l1) over (
      partition by referral_data.term_id
      order by
        referral_data.monday_of_week asc
    ) cum_succeed_l1,
    referral_data.succeed_l2,
    sum(referral_data.succeed_l2) over (
      partition by referral_data.term_id
      order by
        referral_data.monday_of_week asc
    ) cum_succeed_l2,
    user_attend_cnt.tempo,
    user_attend_cnt.user_attend_cnt
  from
    referral_data
    left join user_attend_cnt on referral_data.term_id = user_attend_cnt.term_id
    and referral_data.monday_of_week = user_attend_cnt.monday_of_week
)
,
ever_referral_data as (
  select
    referral_week_data.term_id,
    referral_week_data.monday_of_week,
    count(distinct case when is_enter = 1 then referral_data_tmp.user_id end) as `ever_browser_cnt`,
    count(distinct case when is_save = 1 then referral_data_tmp.user_id end) as `ever_poster_cnt`,
    count(distinct case when is_att = 1 then referral_data_tmp.user_id end) as `ever_att_cnt`,
    count(distinct case when is_upload = 1 then referral_data_tmp.user_id end) as `ever_upload_cnt`
  from
    referral_week_data
    left join user_base on referral_week_data.term_id = user_base.term_id
    left join referral_data_tmp on referral_data_tmp.term_id = user_base.term_id
    and referral_data_tmp.user_id = user_base.user_id
    and referral_week_data.monday_of_week >= referral_data_tmp.monday_of_week
  group by
    referral_week_data.term_id,
    referral_week_data.monday_of_week
)
,
before_class_poster as(
  select
    user_attend_cnt.term_id,
    user_base.term_name,
    date('1990-01-01') as monday_of_week,
    count(distinct user_base.user_id) as user_cnt,
    0 as tempo,
    null as user_attend_cnt,
    count(distinct case when referral_data_tmp.is_enter = 1 then user_base.user_id end) as browser_cnt,
    count(distinct case when referral_data_tmp.is_save = 1 then user_base.user_id end) as poster_cnt,
    count(distinct case when referral_data_tmp.is_upload = 1 then user_base.user_id end) as upload_cnt,
    count(distinct case when referral_data_tmp.is_att = 1 then user_base.user_id end) as att_cnt,
    count(distinct case when referral_data_tmp.is_enter = 1 then user_base.user_id end) as ever_browser_cnt,
    count(distinct case when referral_data_tmp.is_save = 1 then user_base.user_id end) as ever_poster_cnt,
    count(distinct case when referral_data_tmp.is_att = 1 then user_base.user_id end) as ever_att_cnt,
    count(distinct case when referral_data_tmp.is_upload = 1 then user_base.user_id end) as ever_upload_cnt
  from
    user_attend_cnt
    left join user_base on user_attend_cnt.term_id = user_base.term_id
    left join referral_data_tmp on user_base.user_id = referral_data_tmp.user_id
    and user_base.term_id = referral_data_tmp.term_id
    and referral_data_tmp.monday_of_week < user_attend_cnt.monday_of_week
  where
    user_attend_cnt.tempo = 1
  group by
    user_attend_cnt.term_id,
    user_base.term_name
)
,
before_class_l1 as (
  select
    user_attend_cnt.term_id,
    user_base.term_name,
    date('1990-01-01') as monday_of_week,
    count(distinct user_base.user_id) as user_cnt,
    0 as tempo,
    sum(referral_data_tmp.touch_cnt) as reach,
    sum(referral_data_tmp.touch_cnt) as cum_reach,
    sum(referral_data_tmp.invite_l1_cnt) as succeed_l1,
    sum(referral_data_tmp.invite_l1_cnt) as cum_succeed_l1,
    sum(referral_data_tmp.invite_annual_cnt) as succeed_l2,
    sum(referral_data_tmp.invite_annual_cnt) as cum_succeed_l2
  from
    user_attend_cnt
    left join user_base on user_attend_cnt.term_id = user_base.term_id
    left join referral_data_tmp on referral_data_tmp.user_id = user_base.user_id
    and referral_data_tmp.term_id = user_base.term_id
    and referral_data_tmp.monday_of_week < user_attend_cnt.monday_of_week
  where
    user_attend_cnt.tempo = 1
  group by
    user_attend_cnt.term_id,
    user_base.term_name
)
 (select
    before_class_poster.term_id,
    before_class_poster.term_name,
    before_class_poster.monday_of_week,
    before_class_poster.user_cnt,
    before_class_poster.tempo,
    0 as user_attend_cnt,
    before_class_poster.browser_cnt,
    before_class_poster.poster_cnt,
    before_class_poster.upload_cnt,
    before_class_poster.att_cnt,
    before_class_l1.reach,
    before_class_l1.cum_reach,
    before_class_l1.succeed_l1,
    before_class_l1.cum_succeed_l1,
    before_class_l1.succeed_l2,
    before_class_l1.cum_succeed_l2,
    before_class_poster.ever_browser_cnt,
    before_class_poster.ever_poster_cnt,
    before_class_poster.ever_upload_cnt,
    before_class_poster.ever_att_cnt
  from
    before_class_poster
    left join before_class_l1 on before_class_poster.term_id = before_class_l1.term_id
)
union
(
	select
      referral_week_data.term_id,
      referral_week_data.term_name,
      referral_week_data.monday_of_week,
      referral_week_data.user_cnt,
      referral_week_data.tempo,
      referral_week_data.user_attend_cnt,
      referral_week_data.browser_cnt,
      referral_week_data.poster_cnt,
      referral_week_data.upload_cnt,
      referral_week_data.att_cnt,
      referral_week_data.reach,
      referral_week_data.cum_reach,
      referral_week_data.succeed_l1,
      referral_week_data.cum_succeed_l1,
      referral_week_data.succeed_l2,
      referral_week_data.cum_succeed_l2,
      ever_referral_data.ever_browser_cnt,
      ever_referral_data.ever_poster_cnt,
      ever_referral_data.ever_upload_cnt,
      ever_referral_data.ever_att_cnt
    from
      referral_week_data
      left join ever_referral_data on referral_week_data.term_id = ever_referral_data.term_id
      and referral_week_data.monday_of_week = ever_referral_data.monday_of_week
  )
