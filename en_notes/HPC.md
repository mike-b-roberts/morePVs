# HPC

cd ./InputOutput

NB:

* personal storage capacity is 25GB
* Tyrion has 512 cores (64 per node)
* python is installed at /root/opt/python

Additional (shared) space at: `/root/share/scratch/z5044992`

But some issue with passing this to python files as a base bath:

`/share/scratch/z5044992/EN1_rerun/inputs..... does not exist`

To access python:

`module load python/3.6`

To install other packages, set up virtual environment:

```
python3 -m venv /home/z5044992/python_venv
source /home/z5044992/python_venv/bin/activate
```

Then, from within `python_venv` directory,

```
pip install --upgrade pip
pip install pandas
pip install numpy
pip install datetime
deactivate # to exit venv
```

4 virtual environments installed:

```
python_venv
python_venv2
python_venv3
python_venv4
```

__NB:  This seems to remove the restriction on processes > 35:__

`export OPENBLAS_NUM_THREADS=1` 

NB Commented out all `win32` references in `en_utilities` (so `df_to_csv` is now just `df.to_csv`

NB Need to `commit` and `push` all changes to github first, then `git pull` (= `fetch` + `merge`)

Unix paths are different from windows, in particular, path dividers are '/'

* __ Change:__ Use of  "\"  in `study.csv` files, particularly in `pv_filename`
* Move data back out of en folder:
  * Use git to update script,
  * Use `WinSCP` to update data

Location of data folder is in `morePVs/en/data_location.csv`



```
rm -rf .git to remove local git repository
```

### TESTING:



`study_siteJ_bat4_1` 120 scenarios

try on HPC as single process, then as 10 processes:



`qsub` or (BETTER) `sbatch` to submit bash file

`qstat` to look at queue



Getting a `segmentation fault` - related to access,,

from: `python morePVs.py -p EN1a_pv_bat4 -s siteJ_bat4_1 -t False`

try running that line from the command line : still has error finding pv file because of \ vs / issue

p

__NB__ Absolute address (passed to `morePVs.py` as argument `-b`) starts with `/home/z5044992...`

Working batch file is:

```bash
#!/bin/bash
#SBATCH --mail-user=m.roberts@unsw.edu.au
#SBATCH --mail-type=ALL
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8192
#SBATCH --output "/home/z5044992/InputOutput/DATA_EN_3/slurm/slurm-%j.out"
module load python/3.6
source /home/z5044992/python_venv/bin/activate
python morePVs.py -b /home/z5044992/InputOutput/DATA_EN_3 -p for_hpc_example2 -s study_example2_hpc1.csv -t False
deactivate
module unload python/3.6

```



Submit with 

***BUT - VERY SLOW***

* Set up test study , with dynamic calcs, and run with different settings:
  * threads
  * memory
  * number of processors

### `sbatch` and `squeue`



## Timing



`scss_test` 1.6 seconds for 10 (non battery) scenarios on hpc or desktop

`test_bat_numpy` single scenario: dynamic with battery. 

* 

| job number | Execution                                                    | Timing (log)       | Time Use (qstat) | Notes                            |
| ---------- | ------------------------------------------------------------ | ------------------ | ---------------- | -------------------------------- |
|            | desktop, `PyCharm`  no threads                               | 220                |                  |                                  |
|            | desktop, `GitBash` no threads                                | 230                |                  |                                  |
|            | desktop, `GitBash` 6 threads                                 | 223                |                  | (1 scenario: threads irrelevant) |
|            | hpc, single process no threads, `sbatch` <br />(1 task, 4 cpus) | 1175               |                  |                                  |
|            |                                                              |                    |                  |                                  |
|            | hpc, single process, no threads,<br />(1 task, 8 cpus)<br />mem = 8192 | 1165               |                  | single2                          |
|            | hpc ,two process, no threads,<br />(1 task, 4 cpus)<br />mem = 16384 | 1192               |                  | single3                          |
| 2290       | 2 scenarios, no thread, 4 cpus 8192                          | 1174  per scenario |                  | test_bat_numpy2                  |
| 2291       | 2 scenarios, thread, 4 cpus 8192                             | 1226 per scenario  |                  | test_bat_numpy2t                 |
|            | 1 scenario, run on head node                                 | 1148               |                  | test_bat_numpy                   |
|            |                                                              |                    |                  |                                  |
|            |                                                              |                    |                  |                                  |



`study_hpc_test.csv`

- 10 `en_pv` scenarios with central battery and 50 VBs

| job number | Execution                                                    | Timing (log) | Time Use (qstat) | Notes        |
| ---------- | ------------------------------------------------------------ | ------------ | ---------------- | ------------ |
|            | desktop, `PyCharm`  no threads                               |              |                  |              |
|            | desktop, `GitBash` no threads                                |              |                  |              |
|            | desktop, `GitBash` 6 threads                                 |              |                  |              |
|            | hpc, single process no threads, `sbatch` <br />(1 task, 4 cpus) |              |                  |              |
|            | hpc , single process, 6 threads, `sbatch`<br />(1 task, 4 cpus) |              |                  |              |
|            | hpc, single process, no threads,<br />(1 task, 2 cpus)       |              |                  |              |
|            | hpc ,two process, no threads,<br />(1 task, 2 cpus)          |              |                  |              |
|            | hpc ,two process, no threads,<br />(1 task, 2 cpus), mem = 4096 |              |                  | Memory Error |
|            | as above Mem = 16384                                         |              |                  |              |
|            |                                                              |              |                  |              |
|            |                                                              |              |                  |              |
|            |                                                              |              |                  |              |

`study_EN1a_pv_bat4' on hpc, 1 scenario per process:

Approx 600- 700 seconds per scenario. ***All good***



__BUT__ Some failures when importing `numpy` from the virtual environment.  

28/6/18

- this looks like multiple processes trying to import `numpy` simultaneously.
  - Is always `numpy` presumably because it is the first import

__ALSO__ Issue with threading. get rid of threads from `morePVs` script

Introduce pause before submitting jobs:

1. create file `./script` , e.g. 

2. ```
   sbatch /home/z5044992/InputOutput/en/morePVs/bash_files/EN1a_pv_bat4_hpc/siteJ_bat4_2/f000.bat
   sleep 2
   sbatch /home/z5044992/InputOutput/en/morePVs/bash_files/EN1a_pv_bat4_hpc/siteJ_bat4_2/f001.bat
   sleep 2
   ```

   (Make the script executable `chmod a+x ./script` - now included in py file)

   3. execute script file:

   ```ssh
   ./script            # Execute the script!  (Note the use of “./”)
   ```

This has resolved the problem in this instance but does not guarantee no simultaneous imports?

Up to 60 jobs is OK. `sleep 2` may or may not help.

Maybe set `max_jobs` to 60

__DIRECTORY PROBLEM:__ exception caused by 2 processes attempting to create the same directory simultaneously with `os.makedirs` 

 * applies to `/pv` but could also be `/scenarios`, `/outputs` and `/timeseries`
   - [x] Add exception handling for all `makedir` statements ***Resolved***





## Instructions

Copy files to hpc:

* `studies`
* `reference`
* `profiles`



```
$ git pull
$ module load python/3.6
$ source /home/z5044992/python_venv/bin/activate
```

Edit `hpc_setup.py` : 

-   `project`='EN1a_pv_bat4'\
-   `study` = 'siteJ_bat4_2'
-   `maxjobs` = 60

` $ python hpc_setup.py`

`$ chmod a+x ./script`

`$ ./ script` 

`$ python  hpc_recombine.py`



__9/7/18__

running `fill_SGSC_8_hpc.py`: 

* Memory error, increase memory to 16 or 32 (16384 or 32768)
* Segmentation Fault above 35 processes importing pandas

Jobs timed out after 12 hours (my setting in batch file) after filling approx 300 lines of csv (out of 2 x 365).

* 96 processes (x = 0 -> 95)
* 178 lines of .csv per process (er....bad maths! != 17520)
* 24 processes per venv
* 1 core and 16GB per job

Question is whether 96 processes creates issues for the  python/3.6 installation (as opposed to the other packages). i.e should I also pip install python ??

* Each `venv` is 152 MB
* `python` is 192 MB, so why not?

Try with only single python installation: crashes for > 35 processes:

crashes at `import pandas`, even though import is from different `venv`

### Solution:

...is here: `https://stackoverflow.com/questions/51256738/multiple-instances-of-python-running-simultaneously-limited-to-35/51257384#51257384`

```
export OPENBLAS_NUM_THREADS=1
```

Set this in `script` file.

`try 1, 4, 8, 16, 31, 32, 60-64. `

revert to a single `venv` as this doesn't seem to have been the issue.

Run  `hpc_sgsc_setup_1_test.py` with just one line of csv being dealt with by each process,

and 300 processes. 

Try with threads =1

NB Only 52 processes are submitted. the rest are queued

So stick with 48 processes / jobs

But logging files show errors: row numbers getting messed up. Could this be because 2 scripts writing to same log file???? . Set `sleep` to 2s, and include x in logfile name

thread = 1. 

start 15: 29 end 16:29 - 1 hour

thread = 16

start 16:32 end 17:02 - 30 minutes

thread = 32 will cause issues (as previously), so go with 16 for full run:

```
num_threads = 16
# See explanation: `https://stackoverflow.com/questions/51256738/multiple-instances-of-python-running-simultaneously-limited-to-3
num_jobs = 48
interval = int(17520 / num_jobs) + 1
```

- better with `num_jobs =96`

## morePVs - hpc

```
project = EN1_rerun
study = value11
```

10314 scenarios. Average scenario is ?? 30 mins?? (guesstimate) for dynamic scenario on hpc.

Try: 120 processes:  ...approx 48 hours.

Set:

```
time=96:00:00 
cpus-per-task=1
mem=8192

max_jobs=120 (-m)

```

2 issues: 1) it seems to be using threads although `use_threading = False`

​	2) `Disk Quota exceeded`  

Clean up, log thread flag and try again

threading sorted. But still issue with disk quota:

Running ~10,000 scenarios (static), output + input exceeds 25GB, so split into 2 x 5000 studies and remove from hpc between runs. 

Massive space occupied by PV logging, so lose that.

Threading issue returns because i'm running multiple studies Doh. be patient you cock.

## Different Loads: 

17/7/18:

Slicing up the input file has affected the `different_loads` flag as it only looks within the current sliced `stucy_....csv` file. This only affects `customer_results` so is only relevant if looking at individual customer results.

* For `EN3` , use separate study for each site

* For `EN1` and `EN2` `value` studies, I can set `different_loads=True` to save time writing `customer_results` file.

  

`hoc_value11` has `results` output missing for first file (`000`) and `customer_results` missing for 14 files. Why the first one missing? - there was a typo in arrangement for 1 scenario, crashed out.

2 observations:

* DEFINITE speed decrease on hpc if running multiple processes on the same node with the (hpc) threading variable =16. ***Change to 8 threads***
* pass `-t False` to `morePVs.py` doesn't work - variable is false but it still threads. Odd. 
  * because `use_threading` is a string. ***Sorted***

 bat_finance1_I