# Insights Capture Playground
This repo just contains some code for doing various small tasks with Insights Capture, purely built for fun 

<br> 
At the moment, it only contains some code to manage / interact with the backups created by Insights Capture, but eventually I'm sure it'll contain more misc code. Or maybe not who knows. 

# Deps
+ needs `opencv-python` 


## Adding missing videos to Insights Capture 
[add_missing_videos.py](https://github.com/AudIsCool/ic-tooling/blob/main/backup_tooling/add_missing_videos.py) is a script that takes all of the videos in one directory, and adds them to an Insights Capture backup file, which can then be used to restore Insights Capture with those new videos. You can think of it as a drawn out way of importing videos into Insights Capture. 

<br> 

You can find the stand-alone executable [here](https://github.com/AudIsCool/ic-tooling/releases/tag/backup-tooling). 


### Usage 
I'll go over this as if you were using the stand-alone executable provided above. If you're using the script, I'm sure you're smart enough to follow along, if not you can always find me on Discord. 

<br>

Steps: 
1. Download the stand-alone exe and store it somewhere on your PC, your normal download folder is fine
2. Take any videos you'd like to add to Insights Capture, and move them to the folder Insights Capture is using for it's video library (you can see the folder being used in Insights Capture's settings, under the "Video Folder" setting)
3. Open up CMD or Powershell, and cd to the folder you stored the executable in. For example, if you stored the executable in your downloads folder, you'd type in `cd C:/Users/YOUR_WINDOWS_USERNAME_HERE/Downloads`. 
4. In CMD, run the `add_missing_videos.exe` by writing `add_missing_videos.exe` in CMD. 
5. When prompted, paste the path to your video library folder into the app. The app will then generate a new backup file in a new folder called "generate_backup". 
6. Open this file in notepad or any other editor, and copy its contents. 
7. Either edit an existing backup or create a new backup file with the same naming pattern as the existing backups, and paste the contents of the generated backup. 
8. Uninstall Insights Capture (yeah, seriously)
9. Re-Install 
10. Once you open Insights Capture again you'll be prompted with a option to restore. Click restore, and choose the final name you either MADE or EDITED. 
11. Boom, you're done



### Building 
This is mostly a note for myself 
```
pyinstaller -F backup_tooling/add_missing_videos.py --distpath ./dist 
```