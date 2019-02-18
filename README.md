# s2gm-validation

Project to document and maintain all validation methods for S2GM products

The validation of S2GM products comprises 4 levels from L0 to L3

- L0 - Product integrity
    - Check of completeness
    - Check of integrity of files
- L1 - Product plausibility 
    - Visual inspection of RGB (artefacts, hiatus, expected appearance for mosaicking period)
    - Inspection of spectra
    - Assessment of data range
- L2 - Product verification 
    - Difference for SR for different bands
    - Distribution of SR values for both products
    - Distribution of scene classification
    - Distribution of source_index
    - (potential test): Spatial difference for SR for different bands - visual check
- L3 - Product validation
    - Compare number of input products to mosaicking
    - Compare applied algorithm (not possible due to missing band)
    - Compare selected date (same as L2.4 source index)


## Validation metadata

To do the validation certain metadata are required. The main source for these data is 
the file 'validation.json' that has to be available in the root path of the product 
that should be validated.

If the file was not generated, it can be created manually according to the following 
example. Keep in mind that the text '#optional' is not supposed to be in the JSON file.

```
{
	"bands":[
		"B02","B03","B04","B06","B01","B8A","B08","B12","B05","B07","B11","AOT","SCENE","INDEX","SNOW","SUN_ZENITH","VALID_OBS"
	],
	"order_name": "S2GM_valreq_20181119T170905_rand04_T32TNM",      #optional
	"order_id": "4b6a3385-cc0c-4272-aabc-aed9b345fce4",             #optional
	"order_issue_date": "2018-11-19",
	"mosaic_start_date": "2018-01-14",
	"compositing_period": "MONTH",	
	"image_format":	"JP2",
	"resolution": "R20m",
	"projection": "UTM", 
	"tile_ids": [ "T32TNM" ],           #optional
	"mosaic_end_date": "2018-01-31"     #optional
}
```