
def is_passport_match(trulioo_response):
    data_source_result_list = trulioo_response.get('Record', {}).get('DatasourceResults', [])
    dvs_passport_result_search = filter(
        lambda x: x['DatasourceName'] == 'DVS Passport Search',
        data_source_result_list)

    if len(dvs_passport_result_search):
        match_result = dvs_passport_result_search[0]
    else:
        return False

    result_data_source_fields = match_result['DatasourceFields']
    match_keys = [
        'Gender',
        'FirstGivenName',
        'FirstSurName',
        'YearOfBirth',
        'MonthOfBirth',
        'DayOfBirth',
        'PassportNumber'
    ]

    if len(result_data_source_fields) < len(match_keys):
        # Trulioo may return invalid response that not all keys present
        return False

    field_results = []
    for field_obj in result_data_source_fields:
        if field_obj['FieldName'] in match_keys and field_obj['Status'] != 'match':
            match_result = False
            break

    return match_result

