create view code_crack.main.v_decryption_decipher (
	decrypt_id integer, 
	decrypt_date timestamp, 
	caesar_decryption string, 
	rot_13_decryption string, 
	substitution_decryption string, 
	transposition_decryption string, 
		primary key(decrypt_id,decrypt_date)
); 

insert into code_crack.main.v_decryption_decipher 
select distinct 
	caesar_decryption, 
	rot_13_decryption, 
	substitution_decryption, 
	transposition_decryption
from 
	