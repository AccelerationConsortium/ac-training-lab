# Switching from ZIMA default OS to Windows 10
> **Note:** Windows 11 requires a minimum of 64GB of storage, which exceeds the ZIMA default storage capacity of 32GB.  
> **Tip:** To preserve the original ZIMA OS, consider installing Windows on a separate SSD.

### Prerequisites
- **USB Drive**: A USB drive with at least 8GB of storage.
- **Computer with Windows**: A computer running Windows to prepare the USB drive.

## Preparing the USB Drive
Search for `Windows 10 Media Creation Tool` in your browser and download the tool from the official Microsoft website.  
[Download the Windows 10 Media Creation Tool](https://www.microsoft.com/en-ca/software-download/windows10) from the official Microsoft website.

Follow the instructions to create a bootable USB drive:
1. **Insert USB Drive**: Insert the USB drive into your computer.
2. **Run Media Creation Tool**: Open the downloaded tool and accept the license terms.
3. **Select USB Drive**: Choose the option to create installation media (USB flash drive) and select your USB drive from the list.
4. **Download Windows 10**: The tool will download the necessary files and create a bootable USB drive.
5. **Eject USB Drive**: Once the process is complete, safely eject the USB drive from your computer.

> **Note:** The USB drive will be formatted during this process, so ensure you have backed up any important data on it.

## Installing Windows 10 on ZIMA
1. **Insert USB Drive**: Insert the bootable USB drive into the ZIMA device.
2. **Power On ZIMA**: Power on the ZIMA device.
3. **Immediate Repeated Pressing of DEL Key**: As soon as power is plugged in, repeatedly press the `DEL` key to enter the BIOS setup.

> **Note:** You should see the BIOS setup screen at this point. Refer to the image below for a visual reference.

![BIOS Setup Screen](WechatIMG23.jpg)
4. **Select Boot Option**: In the BIOS setup, navigate to the `Boot` tab using the arrow keys.
![BIOS Boot Tab](WechatIMG22.jpg)
5. **Change Boot Order**: Change the boot order to prioritize the USB drive. Use the arrow keys to select the USB drive and move it to the top of the list. Use Enter to select.
![BIOS Boot Order](WechatIMG21.jpg)
> **Note:** The USB drive may be listed as `UEFI USB` or `USB HDD`. Ensure it is set as the first boot device. 

6. **Save and Exit**: Move to the `Save & Exit` tab and select `Save Changes and Reset`. Confirm any prompts to save changes.
![BIOS Save and Exit](WechatIMG20.jpg)

7. **Boot from USB**: The ZIMA device will now boot from the USB drive. Follow the on-screen instructions to install Windows 10.

> **Note:** When prompted to activate Windows, you can skip this step if you don't have a product key. You can activate Windows later.

8. **Installation Type**: Choose the `Custom: Install Windows only (advanced)` option when prompted to select the installation type.
![Windows Installation Type](WechatIMG26.jpg)

9. **Select Partition**: Select the partition where you want to install Windows. If you want to erase the existing OS, select the partition and click `Delete`. This will remove all data on that partition.

> **Warning:** Deleting a partition will erase all data on it. Ensure you have backed up any important data before proceeding.

> **Note:** If you don't want to delete the existing OS, select the existing partitions and delete them. This will create unallocated space for the new installation.
![Windows Partition Selection](WechatIMG25.jpg)
![Windows Partition Deletion](WechatIMG24.jpg)

10 **Wait for Installation**: The installation process will take some time. Your ZIMA device may restart several times during the installation. Follow the on-screen instructions to complete the installation.

> **Note:** After the installation is complete if you are again prompted to install Windows, remove the usb and power cycle the ZIMA device.


## Windows 11

> **Note:** After the installation is complete, you may need to install drivers for your ZIMA device. 

> **Note:** For installation of Windows 11 you will need to turn off `CSM Support` in the `BOOT` tab of the BIOS. `Save Changes and Reset`. Then proceed back to the `SECURITY` tab and turn on `Secure Boot`. `Save Changes and Reset`, before proceeding with the installation of Windows 11.