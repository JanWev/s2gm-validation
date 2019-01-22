'''
This file holds variables provided to ValidationOp.py
'''

refl_bands_dict = {'B01': 'B01','B02': 'B02','B03': 'B03','B04': 'B04','B05': 'B05','B06': 'B06','B07': 'B07',
                   'B08': 'B08','B8A': 'B8A','B11': 'B11','B12': 'B12'}
aux_band_dict = {'AOT': 'quality_aot', 'CLOUD': 'quality_cloud_confidence', 'SNOW': 'quality_snow_confidence',
                 'SCENE': 'quality_scene_classification', 'INDEX': 'source_index', 'MEDOID_MOS': 'medoid_mos',
                 'SUN_ZENITH': 'sun_zenith', 'SUN_AZIMUTH': 'sun_azimuth', 'VIEW_ZENITH_MEAN': 'view_zenith_mean',
                 'VIEW_AZIMUTH_MEAN': 'view_azimuth_mean', 'VALID_OBS': 'valid_obs'}
period_dict = {'DAY': 'D', 'TENDAYS': 'T', 'MONTH': 'M', 'QUARTER': 'Q', 'YEAR': 'Y'}
res_dict = {'R10m': '10','R20m': '20','R60m': '60'}