
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
    passport_result = extract_trulioo_response(trulioo_response, 'DVS Passport Search')
    required_fields = [
        'Gender',
        'FirstGivenName',
        'FirstSurName',
        'YearOfBirth',
        'MonthOfBirth',
        'DayOfBirth',
        'PassportNumber'
    ]
    return test_trulioo_fields_match(passport_result, required_fields)
