with enroll as (select *
                from (select *,
                             row_number() over (partition by term_id,user_id order by user_class_start_time desc ) as rk
                      from htcdm.dws_l1_order_term_learning_renewal_hdf
                      where dt = regexp_replace(date_sub(current_date(), 1), '-', '')
                        and parent_operation_type_name = '9.9'
                        and operation_type_name = '硬件体验课'
                        and subject_id = 11
                        and order_status != 'UNPAID'
                        and substr(pay_time, 1, 10) >= '2023-08-23') as t
                where rk = 1),



    parents_gender as (select order_no,
                              parents_gender
                       from htcdm.dws_trade_order_stat_hdf
                       where dt = regexp_replace(date_sub(current_date, 1), '-', '')),


    login as(
            select
                t1.user_id,
                t1.first_login_os as login_os,
                t1.last_login_time
                from (
                    select
                        user_id,
                        first_login_os,
                        last_login_time,
                        max(last_login_time) over (partition by user_id) as max_last_login_time
                    from htcdm.dws_behav_user_login_original_product_hdf
                    where dt = regexp_replace(date_sub(current_date, 1), '-', '')
                        and login_original_product in ('u3dProgramMortonWindows', 'u3dProgramMortonMAC', 'u3dProgramMortonIOS',
                                                       'u3dProgramMortonAndroid', 'program', 'scratch', 'python', 'cpp',
                                                       'scratchIpad', 'u3dApp', 'scratchJrIpad', 'rutangScratchIpad',
                                                       'rutangProgram', 'rutangU3dApp')
                    ) as t1
            where t1.last_login_time = t1.max_last_login_time
            group by
                t1.user_id,
                t1.first_login_os,
                t1.last_login_time
            )

select en.user_id,
       en.pay_time,
       en.child_age,
       lo.login_os,
       en.parent_operation_type_name,
       en.operation_type_name,
       en.term_name_type,
       en.channel_group_id,
       en.channel_group_name,
       en.enroll_channel_type,
       en.renewal_channel_type,
       en.channel_type_name,
       en.channel_subtype_name,
       en.parents_city_level,
       case pa.parents_gender
           when 0 then '女'
           when 1 then '男'
           else '未知'
       end as parents_gender,
       `if`(en.first_add_counselor_wx_time is not null, 1, 0) as is_add_wx,
       `if`(lo.last_login_time is not null and lo.last_login_time >= en.pay_time, 1, 0) as is_login,
       `if`(en.unit0_attend_time is not null and en.unit0_attend_time <= en.term_start_time, 1, 0) as att_u0, --限开课前到课
       `if`(en.unit1_unlock_attend_datediff between 0 and 6, 1, 0) as att_u1, -- 解锁7天内到首课
       en.is_t6_last_unit_finish as fns_last_unit, -- 解锁7天内完末课
       `if`(en.lastday_renewal_user_cnt is not null, en.lastday_renewal_user_cnt, 0) as is_renewal, -- 限续报结束前续报
       `if`(en.term_renewal_end_time < `current_date`(), 1 ,0) as is_renewal_end
from enroll as en
left join login as lo
    on en.user_id = lo.user_id
left join parents_gender as pa
    on en.order_no = pa.order_no
