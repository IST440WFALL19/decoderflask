--sqlite
--2019-12-03
--smney


--create database code_crack; 
--attach database code_crack <<expr>> as xxxx; 

--person
drop table code_crack.main.person; 

create table code_crack.main.person if not exists (
	person_id integer primary key asc autoincrement, 
	user_id string, 
	password string, 
	first_name string, 
	last_name string, 
	date_added timestamp, 
	date_updated timestamp, 
	password_reset_date timestamp, 
	security_level_cd integer references code_crack.main.zref_security_level(security_level_cd) 
); 

--images
drop table code_crack.main.images; 

create table code_crack.main.images if not exists (
	image_id integer, 
	image_date timestamp, 
	upload_person_id integer references code_crack.main.zref_modules(module_id) , 
	date_added timestamp, 
	date_updated timestamp, 
	image binary, 
	image_jpg_file_loc string, 
		primary key(image_id,image_date)
); 

--image ocr
drop table code_crack.main.image_ocr_details; 

create table code_crack.main.image_ocr_details if not exists (
	ocr_image_id integer primary key asc autoincrement, 
	image_id integer, 
	image_date timestamp, 
	received_from_module_id integer references code_crack.main.zref_modules(module_id), 
	date_added timestamp, 
	date_updated timestamp, 
	image_ocr_text string string, 
		foreign key(image_id,image_date) references code_crack.main.images
); 

--cipher text 
drop table code_crack.main.cipher_text; 

create table code_crack.main.cipher_text if not exists (
	ciphertext_id integer primary key asc autoincrement, 
	ocr_image_id integer references code_crack.main.image_ocr_details(ocr_image_id), 
	received_from_module_id integer references code_crack.main.zref_modules(module_id), 
	date_added timestamp, 
	date_updated timestamp, 
	cipher_text string 
); 















--zref_security_level
drop table code_crack.main.zref_security_level; 

create table code_crack.main.zref_security_level if not exists (
	security_level_cd integer primary key asc, 
	name string,
	date_added timestamp, 
	date_updated timestamp
); 

--zref_modules
drop table code_crack.main.zref_modules; 

create table code_crack.main.zref_modules if not exists (
	module_id integer primary key asc, 
	name string, 
	date_added timestamp, 
	date_updated timestamp
); 