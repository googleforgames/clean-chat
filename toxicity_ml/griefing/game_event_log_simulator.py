
import argparse
import random
import datetime

game_servers = [
'[WTWRP] Deathmatch',
'[WTWRP] Votable',
'Jeffs Vehicle Warfare',
'(SMB) Kansas Public [git]',
'exe.pub | Relaxed Running | CTS/XDF',
'Corcs do Harleys Xonotic Server',
'Jeff & Julius Resurrection Server',
'Odjel za Informatikus Xonotic Server',
'[PAC] Pickup'
]

game_types = [
'Keyhunt',
'Clan Area',
'Deathmatch',
'Capture The Flag',
'Team Death Match',
'Complete This Stage'
]

game_maps = [
'boil',
'atelier',
'implosion',
'finalrage',
'afterslime',
'solarium',
'xoylent',
'darkzone',
'warfare',
'stormkeep'
]

weapons =   1*['Electro'] + \
            1*['Hagar'] + \
            1*['Shotgun'] + \
            1*['Mine Layer'] + \
            1*['Crylink'] + \
            1*['Mortar'] + \
            1*['Blaster'] + \
            1*['Machine Gun'] + \
            1*['Devastator'] + \
            1*['Vortex']

if __name__ == "__main__":
    
    '''
    # ONLY used for TESTING - Example Arguments
    args =  {
                "number_of_records":    10000,
                "output_filename":      "game_event_logs.csv"
            }
    '''
    
    # Arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--number_of_records",  required=True,  default=1000, type=int,     help="Number of records to simulate")
    ap.add_argument("--output_filename",    required=True,                              help="Output filename")
    args = vars(ap.parse_args())
    
    f = open(args['output_filename'],'w')
    f.write('{},{},{},{},{},{},{}\n'.format('datetimestamp','gameid','x_cord','y_cord','points','direction','speed')) 
    counter = 0
    for i in range(args['number_of_records']):
        bias = 1
        datetimestamp = (datetime.datetime.strptime('01-JAN-2019','%d-%b-%Y') + datetime.timedelta(days=int(random.random()*365))).strftime('%Y-%m-%d') + ' {}:{}:{}'.format(str(random.randint(0,23)).zfill(2), str(random.randint(0,59)).zfill(2), str(random.randint(0,59)).zfill(2))
        
        gameid      = int(random.random()*(args['number_of_records']/1000))
        x_cord      = int(random.triangular(0,99, int(99*bias) - random.randint(1,20) ))
        x_cord      = x_cord if x_cord >= 0 else int(random.triangular(0,99, int(99*bias) ))
        y_cord      = int(random.triangular(0,99, int(99*bias) ))
        points      = int(random.random()*1000)
        direction   = int(random.random()*360)
        speed       = int(random.random()*10)
        
        record = '{},{},{},{},{},{},{}\n'.format(datetimestamp, gameid, x_cord, y_cord, points, direction, speed)
        print(record)
        f.write(record)
        counter+=1
    
    f.close()
    
    print(f'''[ INFO ] Successfully wrote {counter} records to {args['output_filename']}''')




#ZEND
