
class VerificationSource(object):
    DVSPASSPORT = 0
    DVSDRIVERLICENSE = 1
    DVSMEDICARECARD = 2
    AUSTRALIAN_ELECTORAL_ROLL = 3
    AUSTRALIAN_CREDIT_AGENCY = 4
    MANUAL_FILE_UPLOAD = 5


VERIFICATION_SOURCES = (
    (VerificationSource.DVSDRIVERLICENSE, 'DVSDriverLicense',),
    (VerificationSource.DVSPASSPORT, 'DVSDriverLicense',),
    (VerificationSource.DVSMEDICARECARD, 'DVSDriverLicense',),
    (VerificationSource.AUSTRALIAN_ELECTORAL_ROLL, 'Australian Electoral Roll',),
    (VerificationSource.AUSTRALIAN_CREDIT_AGENCY, 'Australian Credit Agency',),
    (VerificationSource.MANUAL_FILE_UPLOAD, 'Manual File Upload',),
)


DVS_SOURCE_SET = {
    VerificationSource.DVSDRIVERLICENSE,
    VerificationSource.DVSPASSPORT,
    VerificationSource.DVSMEDICARECARD
}