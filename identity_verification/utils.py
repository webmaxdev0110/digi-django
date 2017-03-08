
def extract_trulioo_response(trulioo_response_dict, data_source_name):
    data_source_result_list = trulioo_response_dict.get('Record', {}).get('DatasourceResults', [])
    filtered_result = filter(
        lambda x: x['DatasourceName'] == data_source_name, data_source_result_list
    )
    if filtered_result:
        return filtered_result[0].get('DatasourceFields')
    else:
        return []

def test_trulioo_fields_match(data_source_results, required_field_list):
    if not len(data_source_results):
        return False

    if len(data_source_results) < len(required_field_list):
        return False

    match_results = []
    for field_obj in data_source_results:
        if field_obj['FieldName'] in required_field_list:
            match_results.append(field_obj['Status'] == 'match')

    # All fields must be match
    return all(match_results)

def is_dvs_driver_license_match(trulioo_response):
    driver_license_result = extract_trulioo_response(trulioo_response, 'DVS Driver License Search')
    required_fields = [
        'DriverLicenceNumber',
        'DriverLicenceState',
        'YearOfBirth',
        'MonthOfBirth',
        'DayOfBirth',
        'FirstGivenName',
        'FirstSurName',
    ]
    return test_trulioo_fields_match(driver_license_result, required_fields)


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

