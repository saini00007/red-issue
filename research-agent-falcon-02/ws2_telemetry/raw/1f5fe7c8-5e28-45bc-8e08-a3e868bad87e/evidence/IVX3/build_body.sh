#!/bin/bash
# build_body.sh <checkvalue> <outfile>
# Builds a multipart/form-data body replicating the exact field set the
# site's own client JS sends to POST /api/send (fname,lname,areacode,tel,
# cname,subject,msg,check,targets).
B="----IVXB$(date +%s%N)"
TGT="info@infinity""capital.bh"   # site's own contact address (form 'targets')
{
printf -- "--%s\r\n" "$B"
printf 'Content-Disposition: form-data; name="fname"\r\n\r\nSecVerify\r\n'
printf -- "--%s\r\n" "$B"
printf 'Content-Disposition: form-data; name="lname"\r\n\r\nIndependent\r\n'
printf -- "--%s\r\n" "$B"
printf 'Content-Disposition: form-data; name="areacode"\r\n\r\n+973\r\n'
printf -- "--%s\r\n" "$B"
printf 'Content-Disposition: form-data; name="tel"\r\n\r\n3600000\r\n'
printf -- "--%s\r\n" "$B"
printf 'Content-Disposition: form-data; name="cname"\r\n\r\nQA\r\n'
printf -- "--%s\r\n" "$B"
printf 'Content-Disposition: form-data; name="subject"\r\n\r\nGeneral Inquiry\r\n'
printf -- "--%s\r\n" "$B"
printf 'Content-Disposition: form-data; name="msg"\r\n\r\nAuthorized security verification of contact endpoint rate limiting. No action needed.\r\n'
printf -- "--%s\r\n" "$B"
printf 'Content-Disposition: form-data; name="check"\r\n\r\n%s\r\n' "$1"
printf -- "--%s\r\n" "$B"
printf 'Content-Disposition: form-data; name="targets"\r\n\r\n%s\r\n' "$TGT"
printf -- "--%s--\r\n" "$B"
} > "$2"
echo "$B"
