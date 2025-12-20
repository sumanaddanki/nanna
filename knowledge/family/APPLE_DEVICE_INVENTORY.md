# Addanke Family - Apple Device Inventory

**Last Updated:** December 20, 2025
**Primary Apple ID:** suman.addanki@gmail.com
**Apple Developer Account:** Gopi Suman Addanke (Team ID: Z64CX539H6)

---

## Family Members

| Member | Role | Primary Device | Apple ID |
|--------|------|----------------|----------|
| **Suman (Semo)** | Head of household | iPhone 15 Pro Max | suman.addanki@gmail.com |
| **Madhuri (Madhu)** | Spouse | iPhone (model TBD) | TBD |
| **Ashru** | Child | iPad (model TBD) | Family Sharing / TBD |

---

## Device Inventory

### 1. Mac Studio (Development Machine)

| Property | Value |
|----------|-------|
| **Owner** | Suman |
| **Model** | Mac Studio (Mac16,9) |
| **Chip** | Apple M4 Max |
| **Serial Number** | KV70VDQ47M |
| **macOS User** | semostudio |
| **Apple ID Signed In** | suman.addanki@gmail.com |
| **Primary Use** | NutriNine development, home server |
| **iCloud Backup** | N/A (Macs don't backup to iCloud, use Time Machine) |
| **Time Machine Backup** | TBD - NEEDS SETUP |

### 2. MacBook Air

| Property | Value |
|----------|-------|
| **Owner** | Suman / Family |
| **Model** | MacBook Air (model TBD) |
| **Chip** | TBD (M1/M2/M3?) |
| **Serial Number** | TBD |
| **macOS User** | TBD |
| **Apple ID Signed In** | TBD |
| **Primary Use** | Portable work, travel |
| **Time Machine Backup** | TBD - NEEDS SETUP |

### 3. Semo's iPhone 15 Pro Max

| Property | Value |
|----------|-------|
| **Owner** | Suman |
| **Model** | iPhone 15 Pro Max (iPhone16,2) |
| **Device Name** | Semo IPhone |
| **CoreDevice UUID** | D497C307-1E73-52C7-ACAE-BBC813202011 |
| **Apple ID Signed In** | suman.addanki@gmail.com |
| **iCloud Backup** | TBD - VERIFY |
| **Storage** | TBD |
| **Color** | TBD |

### 4. Madhuri's iPhone

| Property | Value |
|----------|-------|
| **Owner** | Madhuri |
| **Model** | TBD |
| **Device Name** | TBD |
| **CoreDevice UUID** | TBD (run `xcrun devicectl list devices` when connected) |
| **Apple ID Signed In** | TBD |
| **iCloud Backup** | TBD - VERIFY |
| **Storage** | TBD |

### 5. Ashru's iPad

| Property | Value |
|----------|-------|
| **Owner** | Ashru |
| **Model** | TBD |
| **Device Name** | TBD |
| **Apple ID Signed In** | TBD (Family Sharing recommended) |
| **iCloud Backup** | TBD - VERIFY |
| **Primary Use** | Education, games |
| **Screen Time** | TBD - SETUP RECOMMENDED |

### 6. Suman's Apple Watch Ultra 2

| Property | Value |
|----------|-------|
| **Owner** | Suman |
| **Model** | Apple Watch Ultra 2 (Watch7,5) |
| **Device Name** | Suman's Apple Watch |
| **CoreDevice UUID** | 3A325A3D-1369-5A78-B59D-DDC91173E6B7 |
| **Paired With** | Semo iPhone 15 Pro Max |
| **iCloud Backup** | Via paired iPhone |

---

## Non-Apple Devices (For Reference)

### Samsung S20 FE (Android)

| Property | Value |
|----------|-------|
| **Owner** | Suman (secondary phone?) |
| **Model** | SM-G781V |
| **ADB Serial** | RFCN90WWZLN |
| **Primary Use** | NutriNine Android testing |

---

## iCloud Backup Checklist

### What Gets Backed Up to iCloud (iPhone/iPad):
- App data
- Apple Watch backup (via paired iPhone)
- Device settings
- Home screen and app organization
- iMessage, SMS, MMS
- Photos and videos (if iCloud Photos enabled)
- Purchase history
- Ringtones
- Visual Voicemail password

### What Does NOT Get Backed Up:
- Data already in iCloud (Contacts, Calendars, Notes, iCloud Photos, iMessages)
- Apple Pay info
- Face ID / Touch ID settings
- Apple Mail data
- Music (stored in Apple Music / iTunes)

---

## Backup Verification Steps

### For Each iPhone/iPad:

1. **Check iCloud Backup Status:**
   - Settings > [Your Name] > iCloud > iCloud Backup
   - Verify "Back Up This iPhone/iPad" is ON
   - Check "Last Successful Backup" date

2. **Check iCloud Storage:**
   - Settings > [Your Name] > iCloud > Manage Storage
   - Ensure enough space for all devices

3. **Force a Backup:**
   - Connect to WiFi
   - Settings > [Your Name] > iCloud > iCloud Backup > Back Up Now

### For Each Mac:

1. **Time Machine Setup:**
   - System Settings > General > Time Machine
   - Add backup disk (external drive or NAS)
   - Enable automatic backups

2. **iCloud Drive Sync:**
   - System Settings > [Your Name] > iCloud
   - Enable Desktop & Documents sync (optional)

---

## Recovery Scenarios

### Scenario 1: iPhone Lost/Stolen
1. Use Find My iPhone (icloud.com/find)
2. Mark as Lost or Erase remotely
3. Get new iPhone, restore from iCloud backup during setup

### Scenario 2: iPhone Broken/Replaced
1. Get new iPhone
2. During setup, choose "Restore from iCloud Backup"
3. Select most recent backup
4. Wait for apps to download

### Scenario 3: Mac Needs Reset
1. Ensure Time Machine backup is current
2. Erase Mac (Recovery Mode)
3. Reinstall macOS
4. During setup, choose "Restore from Time Machine"

### Scenario 4: Complete Family Reset
1. Verify ALL devices have current backups
2. Document Apple IDs and passwords (use password manager)
3. Note any 2FA recovery keys
4. Sign out of all devices
5. Restore each device from respective backup

---

## Family Sharing Setup

**Family Organizer:** suman.addanki@gmail.com (recommended)

### Benefits:
- Share App Store purchases
- Share iCloud+ storage (up to 2TB)
- Share Apple Music / Apple TV+ subscriptions
- Screen Time for children
- Location sharing via Find My
- Shared Photo Album

### Setup Steps:
1. Settings > [Your Name] > Family Sharing > Set Up Your Family
2. Invite family members via Apple ID
3. Configure sharing preferences

---

## Action Items

- [ ] Fill in TBD fields when devices are available
- [ ] Verify iCloud backup on Semo's iPhone
- [ ] Get Madhuri's iPhone details and verify backup
- [ ] Get Ashru's iPad details and verify backup
- [ ] Get MacBook Air details
- [ ] Set up Time Machine for Mac Studio
- [ ] Set up Time Machine for MacBook Air
- [ ] Configure Family Sharing if not already done
- [ ] Set up Screen Time for Ashru's iPad
- [ ] Document all Apple ID passwords in secure password manager

---

## DEVSTUDIO Device Registry

These device IDs are used in the DEVSTUDIO deploy script:

```bash
# iOS Devices (CoreDevice UUID from `xcrun devicectl list devices`)
IOS_REGISTRY=(
    "Semo iPhone 15 Pro Max|D497C307-1E73-52C7-ACAE-BBC813202011"
    # "Madhuri iPhone|DEVICE_ID_HERE"  # Add when available
)

# Android Devices (Serial from `adb devices`)
ANDROID_REGISTRY=(
    "Samsung S20 FE|RFCN90WWZLN"
)
```

---

## Notes

- Keep this document updated as devices change
- Review backup status monthly
- Test restore process annually (use old device if available)
