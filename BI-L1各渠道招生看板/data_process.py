def enroll_renewal_data(data) :
    data = data[data['城市等级'].notnull()]
    data = data.drop(['season_order'], axis=1)
    return data