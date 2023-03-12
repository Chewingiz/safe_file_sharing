from Crypto.Util.number import getPrime,inverse
from math import gcd
from hashlib import sha256

def gen_rsa_keypair( bits ):
    e=65537
    size=bits//2 # div entière
    p=getPrime(size)
    q=getPrime(size)
    assert(p!=q)
    n=p*q
    assert(gcd(e,(p-1))==1)
    assert(gcd(e,(q-1))==1)
    phi_n=(p-1)*(q-1)
    assert(e<phi_n and  phi_n % e !=0)
    
    d= inverse(e, phi_n)
    return ((e,n),(d,n))

def rsa (msg, key):
    e,n=key
    assert(msg<n)
    c= pow(msg,e,n)
    return c

def rsa_enc (msg,key):
	return rsa(int.from_bytes(msg.encode('utf-8'), 'big'), key)

def rsa_dec(enc_msg,key):
 	msg=rsa(enc_msg,key)
 	msg=msg.to_bytes((msg.bit_length() + 7) // 8, 'big').decode('utf-8')
 	return msg


def conv_test(msg_a, msg_b):
	key_A = gen_rsa_keypair(64)
	key_B = gen_rsa_keypair(64)

	
	print("Bob souhaite envoyer le message: \""+ msg_a +"\" Alice")
	msg_a_enc = rsa_enc (msg_a, key_A[1])
	
	#print(msg_a_enc )
	msg_a_dec =rsa_dec (msg_a_enc , key_A[0])
	print("Alice reçois le message: \""+ msg_a_dec+"\" de Bob")
	
	msg_b_enc = rsa_enc (msg_b, key_B[0])
	msg_b_dec = rsa_dec (msg_b_enc , key_B[1])


def h ( i ):
	i_bytes=i.to_bytes((i.bit_length() + 7) // 8, 'big') #on passe de int à bytes
	h_int=int.from_bytes(sha256(i_bytes).digest(), 'big')# on hash et on met en int
	return h_int

def rsa_sign (msg, key):
	h_msg=h(msg)
	s=rsa(h_msg,key)#encode avec la clef privée
	return s
	
def rsa_verify(s,key): # renvois 1 si le message est authentique 0 sinon
	s_dec= rsa(s,key)#pow(s,key[0],key[1])
	return s_dec

def conv_test_s(msg_a, msg_b):
	key_A = gen_rsa_keypair(1024)
	key_A_p, key_A_s = key_A 
	
	key_B = gen_rsa_keypair(1024)
	key_B_p,key_B_s = key_B
	
	print("Bob souhaite envoyer le message: \""+ msg_a +"\" signé à Alice")
	msg_a_enc = rsa_enc(msg_a, key_A_s)
	msg_a_s = rsa_sign(msg_a_enc,key_B_p)
	#print(msg_a_s)
	msg_a_enc_s = (msg_a_enc,msg_a_s)
	
	m=msg_a_enc_s[0]
	s=msg_a_enc_s[1]
	
	
	
	if(rsa_verify(s,key_B_s)==h(m)):
		print("Alice reçois le message: \""+ rsa_dec(m,key_A_p) +"\" de Bob")
	else: 
		print("message non authentique " + rsa_dec(m,key_A_p))

"""
if __name__=='__main__':
    print(gen_rsa_keypair(64))
    msg="encode"
    key = gen_rsa_keypair( 64 )
    x = rsa_enc (msg, key[0])
    print(rsa_dec (x, key[1]))
    conv_test("msg_a", "msg_b")
    conv_test_s("msg_a", "msg_b")
"""