import json
import os
import shutil

def get_item_names(path):
	"""Simple function to see items inside the folder."""
	return os.listdir(path)

file_name = "dayz_path.json"

try:
	with open(file_name) as f:
		dayz_path = json.load(f)
except FileNotFoundError:
	#Get DayZ path
	path_origin = input("Paste 'Dayz Addon'-Folder here:")
	#Specify DayZ Server path
	dayZ_server_folder = input("Paste 'Dayz Server'-Folder here:")

	path_origin = os.path.abspath(path_origin)#"Y:/Gaming/1 Steam/steamapps/common/DayZ/!dzsal"
	dayZ_server_folder = os.path.abspath(dayZ_server_folder)

	dayz_path = {
		"path_origin" : path_origin,
		"dayZ_server_folder" : dayZ_server_folder,
		}

	with open(file_name, "w", encoding="utf-8") as f:
		json.dump(dayz_path, f, indent=4)

# path_origin = os.path.abspath(path_origin)#"Y:/Gaming/1 Steam/steamapps/common/DayZ/!dzsal"
# dayZ_server_folder = os.path.abspath(dayZ_server_folder)#"Y:/Gaming/1 Steam/steamapps/common/DayZServer"
new_path_addons = f"{dayz_path['dayZ_server_folder']}/copy_addons_here"
new_path_keys = f"{dayz_path['dayZ_server_folder']}/copy_keys_here"

bat_path = f"{dayz_path['dayZ_server_folder']}/mods_for_start_bat.txt"

mod_folders = get_item_names(dayz_path['path_origin'])
print(f"{len(mod_folders)} mod-folders found.")
raise_confirmation = input("Do you want to start copying the data to the DayZServer-folder? y/n")
raise_confirmation = str(raise_confirmation)

mods_for_bat = ""
failed_copies = []
new_mod_folders = []

if raise_confirmation == "y":

	#check if copy_folders exist if not make some
	if not os.path.isdir(new_path_addons):
		os.makedirs(new_path_addons)
	if not os.path.isdir(new_path_keys):
		os.makedirs(new_path_keys)					

	#copies each folder
	for mod in mod_folders:
		bat_flag = False
		mod_folder = f"{dayz_path['path_origin']}/{mod}"
		
		item_inside_mod_flag = os.path.isdir(mod_folder)

		#create a string to add to batch file to start with server
		print(f"copying {mod} | Items: {item_inside_mod_flag}...", end="")

		#check if folder has items inside
		if item_inside_mod_flag:
			bat_flag = True			
			#copying mod folder to DayZ Server folder
			try:
				shutil.copytree(f"{mod_folder}", f"{dayz_path['dayZ_server_folder']}/{mod}")
			except FileExistsError:
				shutil.rmtree(f"{dayz_path['dayZ_server_folder']}/{mod}")
				shutil.copytree(f"{mod_folder}", f"{dayz_path['dayZ_server_folder']}/{mod}")
				new_mod_folders.append(mod)

			#copying the addons of the mod
			addon_folder = f"{mod_folder}/addons"
			addons = get_item_names(addon_folder)
			for addon in addons:
				shutil.copy(f"{addon_folder}/{addon}", new_path_addons, follow_symlinks=True)

			#copying the keys of the mod
			try:
				key_folder = f"{mod_folder}/keys"
				keys = get_item_names(key_folder)
				for key in keys:
					shutil.copy(f"{key_folder}/{key}", new_path_keys, follow_symlinks=True)
			except FileNotFoundError:
				try:
					key_folder = f"{mod_folder}/key"
					keys = get_item_names(key_folder)
					for key in keys:
						shutil.copy(f"{key_folder}/{key}", new_path_keys, follow_symlinks=True)

				except FileNotFoundError:
					fail_copy = {
						"mod" : mod,
						"reason" : "no key folder"
						}
					failed_copies.append(fail_copy)
					print(f"failed\n")
					bat_flag = False

			if bat_flag:
				#mod string fot "start.bat"
				mods_for_bat += f"{mod};"

				print(f"successfull\n")

		else:
			fail_copy = {
					"mod" : mod,
					"reason" : "no items found inside mod folder"
					}
			failed_copies.append(fail_copy)

			print(f"failed\n")

else:
	print("copy process aborted")

print("Following mods could not be copied:")
for fail_copy in failed_copies:
		print(f"Mod: {fail_copy['mod']}\tReason: {fail_copy['reason']}")

print("Following Mods have been updated:")
for mod in new_mod_folders:
		print(mod)

with open(bat_path, "w") as f:
	f.write(mods_for_bat)

input("Continue with Enter")