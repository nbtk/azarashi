Expand-Archive -Path 'D:\documents\azaraC\azarashiv0.16.1.zip' -DestinationPath 'D:\documents\azaraC\azarashiv0.16.1_ref' -Force
Get-ChildItem -Path 'D:\documents\azaraC\azarashiv0.16.1_ref' -Recurse | Select-Object FullName, Length | Format-Table -AutoSize
