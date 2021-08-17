# Weather Files - process and testing



### Metadata:

__TMY2__ Radiation is in preceding hour. So timestamp is at *end* of the period 

Users manual for TMY2s  (NREL)

Therefore need 

__RMY__

NB `RMY` files start with 1/1/1991 01:00 but this is the *SAME* hour i.e. midnight -> 1am

__IWEC__

"Similar to TMY2"  so ts is end of period???

- start with 00:00 but this is the period 23:00 - 00:00
- this would explain hour difference between IWEC and RMY seen below

## Compare with other WFs

Still, comparing my wf with __RMY__  :

`C:\Users\z5044992\Documents\MainDATA\DATA - Weather\WeatherFiles\en_WFs\comparison of WFs\compare generated wfs with tmy.xlsx`



![1530508772174](C:\Users\z5044992\AppData\Local\Temp\1530508772174.png)



![1530509018774](C:\Users\z5044992\AppData\Local\Temp\1530509018774.png)

and compare with IWEC

![1530509219854](C:\Users\z5044992\AppData\Local\Temp\1530509219854.png)

![1530509097544](C:\Users\z5044992\AppData\Local\Temp\1530509097544.png)



DHI: peaks earlier in MR Wf compared to RMY or IWEC

|          |        | MR WF | RMY   | IWEC  | MR WF | RMY  | IWEC  | MR WF | RMY   | IWEC  |
| -------- | ------ | ----- | ----- | ----- | ----- | ---- | ----- | ----- | ----- | ----- |
| 3 months | Summer | 11:00 | 11:00 | 12:00 |       |      |       | 10:00 | 11:00 | 11:30 |
| 3 months | Winter | 10:30 | 11:00 | 11:30 | 10:00 |      | 11:30 | 10:30 | 11:00 | 11:30 |



## Create Weather File process

WF created by `create_weatherfile_11.1.py`:

```
# v11.1 creates 30-minute weather file , 00, 30 mins
# uses satellite GHI and DNI from e.g mm = 49m
# calcs DHI using irradproc, then fills to 00 & 30
# using 30 min temp & ws
# to give 30min wf
```

PV profile calculated by SAM PVWatts, based on BOM satellite gridded data 

Metadata from: `C:\Users\z5044992\Documents\MainDATA\DATA - Weather\WeatherFiles\en_WFs\meta\en_wf_metadata_cp.csv`

- *Hourly* gridded data: timestamp marks start of period. Data reading is 49.3 minutes (0.82 hours) into hourly period. This `satellite_time`  (in minutes) is fed to `SAM` to calculate `DHI` from `GHI` for weather file. SAM returns DHI, but with timezones on the hour????
- SAM takes solar position on the half-hour for hourly data.
- weather file created with Time Zone =10, first time = 00:00

### Testing

* run site J WF : meta data in `meta\\en_wf_metadata_cp_JONLY.csv`

* interrupt when first WF created (hourly, GHI and DNI only); save wf

  

* interrupt when DHI returned from SAM; save wf

* compare with final hourly and half-hourly wfs

* load raw data into PVSyst and create wf and compare

__Looking at data:__

1) Insolation (GHI and DNI) passed with minutes = 49, no timestamp

2) DHI returned, plus elevation. ( minutes = 49, no timestamp)

3) Interpolation:

 * Interpolates `elevation` which is is stupid when negative

* Data has been shifted on timeline (by 1 hour or by 49 minutes) so

  new timestamp is real, even though old one was nonsense.

  ***Looks to be shifted by 49 minutes***

  ![1530748163901](C:\Users\z5044992\AppData\Local\Temp\1530748163901.png)

* Also elevation has been shifted

![1530748719199](C:\Users\z5044992\AppData\Local\Temp\1530748719199.png)



### Importing into PVSyst

__RMY__

* Reference year. 
* 1st time interval is 0....1 hours (but labeled as 0:0:1)
* ***Time Shift is 1 hour***

Result: Average time shift on clear days = -29 minutes. ***Shift by +29 minutes to resolve***

![1530754682986](C:\Users\z5044992\AppData\Local\Temp\1530754682986.png)

__IWEC__

- Reference year. 
- 1st time interval is 0....1 hours (but labeled as 0:0:1)
- ***Time Shift is 1 hour***

Result: Average time shift on clear days = 0 minutes. 





![1530754499162](C:\Users\z5044992\AppData\Local\Temp\1530754499162.png)



__MR Site J__

* Sequential Dates starting 1/1/13 00:00
* timestamp is start of period
* ***Time shift is zer***

Result: timeshift is -20 minutes. 

(__BUT ALSO__ magnitude difference i.e. x 2 because imported as energy instead of power (W/m2) now corrected:

![1530757006989](C:\Users\z5044992\AppData\Local\Temp\1530757006989.png)



rectify with + 20 mins shift.

![1530757035222](C:\Users\z5044992\AppData\Local\Temp\1530757035222.png)

But still, shift of 1 hour relative to WF (ie insolation at 05:00 in WF is now labelled 04:00)



__Compare MR, RMY, IWEC:__

Total insolation for year:

![1530757391443](C:\Users\z5044992\AppData\Local\Temp\1530757391443.png)

(1 = IWEC, 2= RMY, 3 = MR)

![1530757423186](C:\Users\z5044992\AppData\Local\Temp\1530757423186.png)

See `C:\Users\z5044992\Documents\MainDATA\DATA - Weather\WeatherFiles\en_WFs\comparison of WFs\Compare SiteJ with RMY and IWEC.xlsx` for comparisson data.

## So......:

My WF is all good, but there is a time shift. How to rectify:

Suggestion:

1.  Plot PVsyst meteo WFs. No! Meteo is only monthly totals

2. Look at PV output for standard system for all 3 WFS from SAM and from PVSyst







MR approx 1/2  hour ahead of RMY and approx 1/2 hour behind IWEC



Not so much: approx in sync with RMY but higher insolation.

1 hour behind IWEC

![1530765879964](C:\Users\z5044992\AppData\Local\Temp\1530765879964.png)



- MR sits between RMY and IWEC over the year

```
Have a look at RMY without the hour shift? - doesnt import

Try RMY with first reading 23:00-00:00 - doesn't import

Similarly IWEC
```

###Compare with Solar Zenith Angle from NREL

<https://midcdmz.nrel.gov/solpos/spa.html> 

__SUMMER:__

![1530769305424](C:\Users\z5044992\AppData\Local\Temp\1530769305424.png)



__WINTER:__

![1530769357844](C:\Users\z5044992\AppData\Local\Temp\1530769357844.png)



- MR data appears to be ahead by approx 1/2 hour
- __AUTUMN:__
- ![1530769445815](C:\Users\z5044992\AppData\Local\Temp\1530769445815.png)

__SPRING:__

![1530769482140](C:\Users\z5044992\AppData\Local\Temp\1530769482140.png)



This is all in: `C:\Users\z5044992\Documents\MainDATA\DATA - Weather\WeatherFiles\en_WFs\comparison of WFs\Compare SiteJ with RMY and IWEC.xlsx`

### But...



More useful to look at single day:

![1530829369295](C:\Users\z5044992\AppData\Local\Temp\1530834623723.png)

![1530834724507](C:\Users\z5044992\AppData\Local\Temp\1530834724507.png)



![1530834769470](C:\Users\z5044992\AppData\Local\Temp\1530834769470.png)

__So, MR WF aligns pretty well with zenith angle. Maybe -15mins__

Look at RMY and IWEC:

IWEC not as good, but at least partly because of timestamp referencing end of period:

![1530831264433](C:\Users\z5044992\AppData\Local\Temp\1530831264433.png)

RMY  OK *despite* referencing end of period

![1530831325552](C:\Users\z5044992\AppData\Local\Temp\1530831325552.png)



## So....

* SOME of the difference is due to:

  * Difference between MR and IWEC is largely due to different timestamp labelling, plus:

  * diff between MR and RMY is because of SAM choosing zenith for middle of time period , so putting RMY out of whack, but is OK for MR because minutes are specified.... I think:

  * Check with SAM documentaion:

    ```
    SAM's photovoltaic model determines the time for sun position calculations as follows:•For hourly data with no Minute column, the sun position is for the midpoint of the hour. For the sunrise time step, the sun position is at the midpoint between sunrise time and the end of the time step. Similarly, for the sunset hour, the sun position is the midpoint between the beginning of the time step and sunset time.•For hourly data with a Minute column and sub-hourly data (which must have a Minute column), use the minute value as the time for the sun position calculation for all hours, including the sunrise and sunset hours.
    ```

    Also, btw:

    `In weather files from the [NREL National Solar Radiation Database](https://nsrdb.nrel.gov/), the irradiance data is measured instantaneously with the following time conventions:  - TMY data is measured at the beginning of the hour  - Single-year data is measured at the midpoint of the hour  - 30-minute data is measured at the beginning of each 30-minute time step (beginning and midpoint of the hour)  - Data from the older datasets (TMY3 and TMY2) assume irradiance data is the total radiation received over the entire hour.`



## But......

When I import my weather file into PVSyst, it is 20 minutes ahead of the clearsky model:

 

 Which can be shifted + 20 to align: ![img](file:///C:/Users/z5044992/AppData/Local/Temp/msohtmlclip1/01/clip_image002.jpg)                                                                                                                                                                                                                                                                                                                                                                                                                                                                

 

![img](file:///C:/Users/z5044992/AppData/Local/Temp/msohtmlclip1/01/clip_image003.png)

AND comparing my weather file to the solar position data, my data seems to be 15-20 mins ahead of the solar position 

![img](file:///C:/Users/z5044992/AppData/Local/Temp/msohtmlclip1/01/clip_image005.jpg)![img](file:///C:/Users/z5044992/AppData/Local/Temp/msohtmlclip1/01/clip_image007.jpg)

 

__SO:__ WF needs to be shifted by +20 minutes.

look at python file.

Interpolation seems to work:

![1530838445232](C:\Users\z5044992\AppData\Local\Temp\1530838445232.png)

`C:\Users\z5044992\Documents\MainDATA\DATA - Weather\WeatherFiles\en_WFs\comparison of WFs\check interpolation.xlsx`

__BUT NO IT F***ING DOESN'T__

pandas.interpolate (method = 'linear'): `‘linear’: ignore the index and treat the values as equally spaced. `Doh!

So, use: 

* Try a couple of options to do this 

in  `create_weatherfile_12_1.py`  :

* Try 30 minutes instead of 49. Very odd results. insolation starts earlier 4am and finishes later. all gone to cock

* Try 10 mins. With 10 hour tz it's ungood

* Try  10 mins with tz =9. same as previous

  Tried 49minutes for zenith with 29 for delta t and it revealed that the `pd.interpolate` was defaulting to `method = 'linear'` when it should be `method = 'index'` .

  * so now try original (tz = 10, minutes = 49, delta t = 49) with correct interpolation AND......

![1530928491841](C:\Users\z5044992\AppData\Local\Temp\1530928491841.png)





![1530928499487](C:\Users\z5044992\AppData\Local\Temp\1530928499487.png)

![1530928505644](C:\Users\z5044992\AppData\Local\Temp\1530928505644.png)



....it *looks* more aligned, although there could still be an issue at sunrise / sunset.



Update this in `create_weatherfile_13.py`

Try this new one in PVSyst: it is shifted by -16 minutes

so try also: 10,49,29 and 10, 33,33 and 10,5,5 and 9,5,5. They are all far more to cock



Unshifted:

![1530934223071](C:\Users\z5044992\AppData\Local\Temp\1530934223071.png)

Shifted +16:

- THIS IS GOOD! PVSyst uses zenith at midpoint of data (ie 00:15 and 0045). SAM doesnt so, these files are aligned for use in SAM provided a minute column is passed.
- 



## PV profiles

This is done in `C:\Users\z5044992\Documents\MainDATA\DATA_EN_4\pv_profiles\pv metadata\en3_pv_metadata.csv`
NB pv is created by: `C:\PYTHONprojects\utilities\create_pv_profile_subarrays.py`
and stored in `C:\Users\z5044992\Documents\MainDATA\DATA_EN_4\pv_profiles\vb_pv`

compare old and new (eg Site A max):

![1531449488721](C:\Users\z5044992\AppData\Local\Temp\1531449488721.png)

