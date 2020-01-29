import os
import platform
import shutil
import stat

OS_WIN = 1
OS_LINUX = 2
OS_OTHER = 3


def get_platform(raw=False):
    '''
    :return:  "Windows" or "Linux"
    '''
    s = platform.system()
    if raw:
        return s

    info = {"Windows": OS_WIN, "Linux": OS_LINUX}

    return info.get(s, OS_OTHER)


def get_os_arch():
    '''
    :return: 'AMD64' or 'x86_64', return "" if not sure.
    '''
    return platform.machine()


def get_os_hostname():
    '''
    :return: The Computer's hostname
    '''
    return platform.node()


def get_os_ver():
    '''
    :return: OS version, such as "Windows-10", "Linux-2.6.32"
    '''
    return platform.platform(terse=True)


def get_processor():
    '''
    :return: cpu info: eg. "Intel64 Family 6 Model 78 Stepping 3, GenuineIntel" if is winOS
    '''
    return platform.processor()


def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), 'Desktop')


def del_read_only_file(fpath):
    """
    :param fpath: path for file or folder
    """
    if os.path.exists(fpath):
        if os.path.isfile(fpath):
            try:
                os.remove(fpath)
            except:
                os.chmod(fpath, stat.S_IWRITE)
                os.remove(fpath)
        elif os.path.isdir(fpath):
            try:
                shutil.rmtree(fpath)
            except:
                os.chmod(fpath, stat.S_IWRITE)
                shutil.rmtree(fpath)


if __name__ == '__main__':
    print(get_os_arch())
    print(get_os_hostname())
    print(get_os_ver())
    print(get_processor())
    print(get_desktop_path())
