import os
import ftplib
import ftputil
from pathlib import Path


def ftp_upload(ftp_host, src_path, dst_path=None):
    if dst_path is None:
         ftp_host.path.join(os.curdir)

    # Make sure that local path is a directory
    if src_path.is_dir():
        # Make sure that the root path exists
        if ftp_host.path.exists(dst_path) is False:
            # Inform user
            print(f'mkdir: {src_path} -> {dst_path}')

            # Create folder
            ftp_host.mkdir(dst_path)

        # Parse content of the root folder
        for src_child in src_path.iterdir():
            if src_child.is_dir():
                # Use recursion for sub folders/files
                dst_child = ftp_host.path.join(dst_path, src_child.stem)
                ftp_upload(ftp_host, src_child, dst_child)

            else:
                # Copy sub files
                dst_child = ftp_host.path.join(dst_path, src_child.name)

                # Inform user
                print(f'upload: {src_child} -> {dst_child}')

                # Perform copy (upload)
                ftp_host.upload(src_child, dst_child)
                # ftp_host.upload_if_newer(src_child, dst_child)

    else:
        # Inform user
        print(f"src_path: '{src_path}' must be an existing directory!")


if __name__ == '__main__':
    # FTP settings
    user = "pi"
    password = "pi123456"
    host = "192.168.43.43"
    port = 21

    # Path settings
    src_path = Path(__file__).parent.resolve() / "data"
    dst_dir = "data"

    # Inform user
    print(f"Establishing FTP session as '{user}'")

    # Establish FTP session
    ftplib.FTP.port = port
    with ftputil.FTPHost(host, user, password) as ftp_host:
        # Perform recursive FTP upload
        dst_path = ftp_host.path.join(os.curdir, dst_dir)
        ftp_upload(ftp_host, src_path, dst_path)
