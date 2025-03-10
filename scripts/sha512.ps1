(Get-FileHash -Path ./dist/v0.1-rc4/goes_dl-0.1rc4.tar.gz -Algorithm SHA512).hash > ./dist/v0.1-rc4/goes_dl-0.1rc4.tar.gz.sha512.txt
(Get-FileHash -Path ./dist/v0.1-rc4/goes_dl-0.1rc4-py3-none-any.whl -Algorithm SHA512).hash > ./dist/v0.1-rc4/goes_dl-0.1rc4-py3-none-any.whl.sha512.txt
