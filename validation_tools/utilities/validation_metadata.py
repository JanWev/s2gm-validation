

def get_required_file_prefixes(test_metadata):

    file_prefixes = []

    requestable_bands = {
        'B01': 'B01',
        'B02': 'B02',
        'B03': 'B03',
        'B04': 'B04',
        'B05': 'B05',
        'B06': 'B06',
        'B07': 'B07',
        'B08': 'B08',
        'B11': 'B11',
        'B12': 'B12',
        'B8A': 'B8A',
        'AOT': 'quality_aot',
        'CLOUD': 'quality_cloud_confidence',
        'SNOW': 'quality_snow_confidence',
        'SCENE': 'quality_scene_classification',
        'INDEX': 'source_index',
        'MEDOID_MOS': 'medoid_mos',
        'SUN_ZENITH': 'sun_zenith',
        'SUN_AZIMUTH': 'sun_azimuth',
        'VIEW_ZENITH_MEAN': 'view_zenith_mean',
        'VIEW_AZIMUTH_MEAN': 'view_azimuth_mean',
        'VALID_OBS': 'valid_obs',
    }

    if not test_metadata['image_format'].lower() == 'netcdf':
        file_prefixes.append('metadata')

        for b in test_metadata['bands']:
            file_prefixes.append(requestable_bands[b])

    return file_prefixes