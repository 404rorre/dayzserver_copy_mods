import json
import os
import shutil
from operator import itemgetter



def get_item_names(path):
	"""Simple function to see items inside the folder."""
	return os.listdir(path)

def universal_path_from_input(msg_helper):
	"""
	Simple function to make a clear path usable for linux and windows cmd
	after input of request.
	"""
	return os.path.abspath(input(msg_helper))

def get_json_file(file_name):
	"""Function to search for save file and create a new one when not existing."""
	with open(file_name) as f:
		return json.load(f)

def get_dayz_folder_paths(file_name):
	try:	
		dayz_path = get_json_file(file_name)
	except FileNotFoundError:
		dayz_path = dump_json_dict(
		file_name,
		dayz_mod_folder=universal_path_from_input(
										"Paste 'Dayz Addon'-Folder here:"),
		dayZ_server_folder=universal_path_from_input(
										"Paste 'Dayz Server'-Folder here:"),
			)
	return dayz_path["dayz_mod_folder"], dayz_path["dayZ_server_folder"]

def dump_json_dict(file_name, **kwargs):
	"""
	Simple function to create dictionary and dump files as json file.
	"""
	with open(file_name, "w", encoding="utf-8") as f:
		json.dump(kwargs, f, indent=4)
	return kwargs

def dump_list(list_hlp, list_name):
	"""
	Simple function which dumps list into text file.
	Can be copied into start.bat to start with special mods for server init.
	"""
	with open(list_name, "w") as f:
		f.write(list_hlp)

def report_fail(mod=None, error_report=None, report=True):
	"""Simple mod to create dictionary about reasons why copying failed."""
	global copy_fails
	errors = {
		1 : "no items",
		2 : "no key folder",
		}
	if report:
		copy_fail = {
					"mod" : mod,
					"error" : int(error_report),
					}
		copy_fails.append(copy_fail)
	else:
		copy_fails = sorted(copy_fails, key=itemgetter("error"),
							reverse=True)

		print("Following mods could not be copied:")
		for copy_fail in copy_fails:
			print(f"Error: {errors[copy_fail['error']]}\t"
					f"Mod: {copy_fail['mod']}")


def copy_items_list(path_copy_from, path_extension, path_copy_to):
	"""Simple function to copy items from one folder to another."""
	items_folder = f"{path_copy_from}/{path_extension}"
	items = get_item_names(items_folder)
	for item in items:
		shutil.copy(f"{items_folder}/{item}", path_copy_to, 
			follow_symlinks=True)

def copy_folders(path_copy_from, path_extension, path_copy_to):
	"""Simple function to copy folders to another location."""
	try:
		shutil.copytree(path_copy_from, f"{path_copy_to}/{path_extension}")
	except FileExistsError:
		shutil.rmtree(f"{path_copy_to}/{path_extension}")
		shutil.copytree(path_copy_from, f"{path_copy_to}/{path_extension}")
		new_mod_folders.append(path_extension)

def copy_mod_keys(mod_folder, new_path_keys):
	"""
	Simple function to test for different naming of key folders
	and creating warning if not existing.
	"""
	try:
		copy_items_list(mod_folder, "keys", new_path_keys)
		return True			
	except FileNotFoundError:
		try:
			copy_items_list(mod_folder, "key", new_path_keys)
			return True
		except FileNotFoundError:
			print(f"failed\n")
			report_fail(mod, 2)
			return False

@dump_list
@report_fail(report=True)
def dump_report():
	"""Simple function to dump report as txt file."""


file_name, mods_for_bat = "dayz_path.json", ""
copy_fails, new_mod_folders =[], []

dayz_mod_folder, dayZ_server_folder = get_dayz_folder_paths(file_name)
new_path_addons = f"{dayZ_server_folder}/copy_addons_here"
new_path_keys = f"{dayZ_server_folder}/copy_keys_here"

#gets list of all mods inside folder
mods = get_item_names(dayz_mod_folder)
print(f"{len(mods)} mod-folders found.")
raise_confirmation = str(input(
	"Do you want to start copying the data to the DayZServer-folder? y/n"))



if raise_confirmation == "y":
	#check if copy_folders exist if not make some
	if not os.path.isdir(new_path_addons):
		os.makedirs(new_path_addons)
	if not os.path.isdir(new_path_keys):
		os.makedirs(new_path_keys)					

	#copies each folder
	for mod in mods:
		bat_flag = False
		mod_folder = f"{dayz_mod_folder}/{mod}"
		
		#check if folder has items inside
		item_inside_mod_flag = os.path.isdir(mod_folder)
		#create a string to add to batch file to start with server
		print(f"copying {mod} | Items: {item_inside_mod_flag}...", end="")
		#start copying
		if item_inside_mod_flag:			
			#copying mod folder to DayZ Server folder
			copy_folders(mod_folder, mod, dayZ_server_folder)
			#copying the addons of the mod
			copy_items_list(mod_folder, "addons", new_path_addons)			
			#copying the keys of the mod
			bat_flag = copy_mod_keys(mod_folder, new_path_keys)
			#continues copying if bat_flag True (copying successfull)
			if bat_flag:
				#mod string fot "start.bat"
				mods_for_bat += f"{mod};"
				print(f"successfull\n")
		else:
			print(f"failed\n")
			report_fail(mod, 1)
else:
	print("copy process aborted")


report_fail(report=False)
		

print("Following Mods have been updated:")
for mod in new_mod_folders:
		print(mod)

dump_list(mods_for_bat, "mods_for_start_bat.txt")

input("Continue with Enter")