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

--translate language
drop table code_crack.main.image_translate_language

create table code_crack.main.image_translate_language if not exists ( 
	image_language_id integer primary key asc autoincrement, 
	ciphertext_id integer references code_crack.main.cipher_text(ciphertext_id), 
	received_from_module_id integer references code_crack.main.zref_modules(module_id), 
	date_added timestamp, 
	date_updated timestamp, 
	original_language string, 
	converted_language string, 
	language_technique_cd integer references code_crack.main.zref_language_technique(language_technique_cd)
); 

--caesar
drop table code_crack.main.caesar_decryption

create table code_crack.main.caesar_decryption if not exists ( 
	caesar_id integer primary key asc autoincrement, 
	image_language_id integer references code_crack.main.image_translate_language(image_language_id), 
	received_from_module_id integer references code_crack.main.zref_modules(module_id), 
	caesar_decryption string, 
	date_added timestamp, 
	date_updated timestamp, 
	decryption_technique_cd integer references code_crack.main.zref_decryption_technique(decryption_technique_cd)
); 

--rot 13
drop table code_crack.main.rot_13_decipher;

create table code_crack.main.rot_13_decipher if not exists ( 
	rot_13_decipher_id integer primary key asc autoincrement, 
	image_language_id integer references code_crack.main.image_translate_language(image_language_id), 
	received_from_module_id integer references code_crack.main.zref_modules(module_id), 
	rot_13_decipher string, 
	date_added timestamp, 
	date_updated timestamp, 
	decryption_technique_cd integer references code_crack.main.zref_decryption_technique(decryption_technique_cd)
); 

--substitution
drop table code_crack.main.substitution_decipher;

create table code_crack.main.substitution_decipher if not exists ( 
	substitution_decipher_id integer primary key asc autoincrement, 
	image_language_id integer references code_crack.main.image_translate_language(image_language_id), 
	received_from_module_id integer references code_crack.main.zref_modules(module_id), 
	substitution_decipher string, 
	date_added timestamp, 
	date_updated timestamp, 
	decryption_technique_cd integer references code_crack.main.zref_decryption_technique(decryption_technique_cd)
); 

--transpose
drop table code_crack.main.transposition_decipher;

create table code_crack.main.transposition_decipher if not exists ( 
	transposition_decipher_id integer primary key asc autoincrement, 
	image_language_id integer references code_crack.main.image_translate_language(image_language_id), 
	received_from_module_id integer references code_crack.main.zref_modules(module_id), 
	transposition_decipher string, 
	date_added timestamp, 
	date_updated timestamp, 
	decryption_technique_cd integer references code_crack.main.zref_decryption_technique(decryption_technique_cd)
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

--zref_language_technique
drop table code_crack.main.zref_language_technique; 

create table code_crack.main.zref_language_technique if not exists (
	language_technique_cd integer primary key asc, 
	name string, 
	date_added timestamp, 
	date_updated timestamp
); 

--zref_decryption_technique
drop table code_crack.main.zref_decryption_technique; 

create table code_crack.main.zref_decryption_technique if not exists (
	decryption_technique_cd integer primary key asc, 
	name string, 
	date_added timestamp, 
	date_updated timestamp
); 