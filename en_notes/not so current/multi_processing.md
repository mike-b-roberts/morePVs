## Adding threading to morePVs

1) Create new branch
2) Set up test file, run it and save results foir comparisson
3) Add threading:
* start from here: https://stackoverflow.com/questions/43531510/speeding-up-iterative-process-with-pandas-dataframe


1) tick
2) `study_test7.csv` (Use `study_test7a.csv` for threading anc compare)

Test script is `firstthreading.py` in `en_bits_and_bobs`
* it works
* Need to think about where to split the morePVs script and what happens if scripts finish in a different order to starting.:
* obvious answer is run a thread for each scenario:
    -   `scenario.logScenarioData()` - could be aproblem if different threads are accessing `study.op` or other files.
    - put a `Lock` around this function.
    - also make study a global variable
    - also put a `lock around `study.study_parameterss.loc[self.name,c] = study.study_parameterss.loc[self.name,'all_residents']' in `scenario.__init__`
    - issue with conflict as threads are called `t` - change to `this_thread`
    
 Two issues: 
 * it's hanging at the end, the lock maybe is causing an issue with eth final logging routine?
 * issue in line 925 : `if any(word in self.tariff_lookup.loc[t, 'tariff_type'] for word in ['Block','block','Dynamic','dynamic'])]`
 
 - This highlights an inefficiency: If all households have teh same tariff, the tariff  is copied to them all, then added to teh `tariffs_in_use` list, e.g., 208 times and then duplicates removed. Doh!.
 But, more important is a `nan` has appeared, presumably because of multiple threads accessing `study.study_parameterss'.
 
 - Perhaps one thread is writing to `study.syudy_parameters` while another is reading. Perhaps it is possible to eliminate all writing to 
 `study` by copying `study.study_parameterss` to a `Scenario.` variable??
 
 NOW works as far as the end then hangs, After `Study.logStudyData`
 - something to do with the try: except:
 
 
 This now fixed using `concurrent.futures.ThreadPoolExecutor` as advised here: https://stackoverflow.com/questions/49743879/python-script-is-hanging-after-multithreading
 
 Try different numbers of threads:
 (NB there is another script asos running concurrently)

|   |                    start  |                       end   |         time   |
|---|---------------------------| ----------------------------|----------------|
|2  |2018-04-10 12:01:33.329473 | 2018-04-10 12:03:09.607100  | 0:01:36.277627 |
|4  |2018-04-10 12:03:09.608100 | 2018-04-10 12:04:47.406879  | 0:01:37.798779 |
|6  |2018-04-10 12:04:47.407879 | 2018-04-10 12:06:27.582895  | 0:01:40.175016 |
|8  |2018-04-10 12:06:27.583895 | 2018-04-10 12:08:08.233959  | 0:01:40.650064 |
|10 |2018-04-10 12:08:08.234960 | 2018-04-10 12:10:01.029238  | 0:01:52.794278 |
|15 |2018-04-10 12:10:01.030238 | 2018-04-10 12:11:43.075441  | 0:01:42.045203 |


It seems to make very little difference, goddamnit. PERHAPS, it needs to be parallel processes rather than threads??? No. THESE ARE ALL with 6 threads. Run again 
(NB only 12 scenarios, so n=15 is actually n=12)

|   |                    start---|                     end    |         time   |
|---|----------------------------|----------------------------|----------------|
|2  | 2018-04-10 18:12:11.961353 | 2018-04-10 18:14:06.488805 | 0:01:54.527452
|4  | 2018-04-10 18:14:06.488805 | 2018-04-10 18:15:41.699325 | 0:01:35.210520
|6  | 2018-04-10 18:15:41.700325 | 2018-04-10 18:17:18.608015 | 0:01:36.907690
|8  | 2018-04-10 18:17:18.609015 | 2018-04-10 18:19:04.559609 | 0:01:45.950594
|10 | 2018-04-10 18:19:04.560609 | 2018-04-10 18:20:54.784631 | 0:01:50.224022
|15 | 2018-04-10 18:20:54.785631 | 2018-04-10 18:22:54.483599 | 0:01:59.697968

Try running old (Master Branch version) without threading
but bearing in mind that i'm running team viewer which may increase times
0:02:48.272826
0:02:45.011500

But threading with Team Viewer running:
                         start                         end            time
2   2018-04-10 20:07:36.601748  2018-04-10 20:09:32.231310  0:01:55.629562
4   2018-04-10 20:09:32.232310  2018-04-10 20:11:08.509937  0:01:36.277627
6   2018-04-10 20:11:08.510937  2018-04-10 20:12:47.963881  0:01:39.452944
8   2018-04-10 20:12:47.964881  2018-04-10 20:14:34.445528  0:01:46.480647
10  2018-04-10 20:14:34.446529  2018-04-10 20:16:28.053888  0:01:53.607359
15  2018-04-10 20:16:28.054888  2018-04-10 20:18:30.451127  0:02:02.396239

__LOOKS LIKE 6 THREADS IS OPTIMUM__ (for 12 scenarios). 

Try again (without TeamnViewer running)
and then again for 36 scenarios
                        start                         end            time
2  2018-04-11 09:26:23.679276  2018-04-11 09:28:18.382746  0:01:54.703470
3  2018-04-11 09:28:18.382746  2018-04-11 09:29:55.411448  0:01:37.028702
4  2018-04-11 09:29:55.412448  2018-04-11 09:31:31.413047  0:01:36.000599
5  2018-04-11 09:31:31.414047  2018-04-11 09:33:08.697774  0:01:37.283727
6  2018-04-11 09:33:08.698774  2018-04-11 09:34:49.175821  0:01:40.477047
8  2018-04-11 09:34:49.176821  2018-04-11 09:36:47.224625  0:01:58.047804

For 36 scenarios:
                        start                         end            time
4   2018-04-11 09:44:45.355433  2018-04-11 09:48:39.659861  0:03:54.304428
6   2018-04-11 09:48:39.660861  2018-04-11 09:52:25.657459  0:03:45.996598
8   2018-04-11 09:52:25.658459  2018-04-11 09:56:46.997590  0:04:21.339131
10  2018-04-11 09:56:46.997590  2018-04-11 10:01:37.481636  0:04:50.484046
12  2018-04-11 10:01:37.482636  2018-04-11 10:06:49.320816  0:05:11.838180
15  2018-04-11 10:06:49.320816  2018-04-11 10:12:40.220903  0:05:50.900087
20  2018-04-11 10:12:40.220903  2018-04-11 10:19:02.027080  0:06:21.806177

On this basis, use 6 threads.

13/4/18: Another test comparing threads and processes: 
At least some of the above was carried out with multi-process rather than multi-threading

With 12 scenarios: Swap `ThreadPoolExexutor` with `ProcessPoolExecutor`:

`ProcessPoolExecutor`:
                         start                         end            time
4   2018-04-13 17:54:10.811711  2018-04-13 17:55:43.442447  0:01:32.630736
6   2018-04-13 17:55:43.442447  2018-04-13 17:57:18.258964  0:01:34.816517
8   2018-04-13 17:57:18.258964  2018-04-13 17:59:00.831694  0:01:42.572730
10  2018-04-13 17:59:00.832694  2018-04-13 18:00:50.344694  0:01:49.512000
12  2018-04-13 18:00:50.344694  2018-04-13 18:02:49.210694  0:01:58.866000
15  2018-04-13 18:02:49.210694  2018-04-13 18:04:50.421694  0:02:01.211000
20  2018-04-13 18:04:50.422694  2018-04-13 18:06:51.691694  0:02:01.269000

`ThreadPoolExexutor`:
                         start                         end            time
4   2018-04-13 18:07:18.590694  2018-04-13 18:08:51.184694  0:01:32.594000
6   2018-04-13 18:08:51.185694  2018-04-13 18:10:25.680694  0:01:34.495000
8   2018-04-13 18:10:25.681694  2018-04-13 18:12:07.896694  0:01:42.215000
10  2018-04-13 18:12:07.896694  2018-04-13 18:13:57.776694  0:01:49.880000
12  2018-04-13 18:13:57.777694  2018-04-13 18:15:54.834694  0:01:57.057000
15  2018-04-13 18:15:54.834694  2018-04-13 18:17:56.879293  0:02:02.044599
20  2018-04-13 18:17:56.880293  2018-04-13 18:19:57.820386  0:02:00.940093

Wow - almost identical. 


Multi- Processing from git bash console
---------------------------------------
Using `try_args.py` from `git bash`
cd /C/PYTHONprojects/en
`python try_args.py -p EN1_value_of_pv -s siteD_value2 $`
NB `&` creates non-consecutive processes

Run 7 processes. Each process up to 6 threads, but maybe that's a mistake.
Issues with logging, I suspect because the filenames are the same. Rename logfiles to include seconds.

create `bat` file to run from single bash line


