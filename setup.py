import pip

def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

# Example
if __name__ == '__main__':
    install('speedtest-cli')
    install('pytube3')
    install('numpy')
    install('requests')
    install('cv2')
