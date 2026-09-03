#!/bin/bash

set -euo pipefail

usage() {
  printf 'Usage: %s < message.txt\n' "$0"
  printf 'Copies non-empty UTF-8 text from standard input to the macOS clipboard.\n'
}

if (( $# == 1 )) && [[ $1 == "-h" || $1 == "--help" ]]; then
  usage
  exit 0
fi

if (( $# != 0 )); then
  usage >&2
  exit 2
fi

if [[ -t 0 ]]; then
  usage >&2
  exit 2
fi

/usr/bin/osascript -l JavaScript -e '
ObjC.import("Foundation");
ObjC.import("AppKit");

const input = $.NSFileHandle.fileHandleWithStandardInput.readDataToEndOfFile;
if (Number(input.length) === 0) {
  throw new Error("no message was provided on standard input");
}

const message = $.NSString.alloc.initWithDataEncoding(
  input,
  $.NSUTF8StringEncoding,
);
if (message.isNil()) {
  throw new Error("standard input is not valid UTF-8 text");
}

const pasteboard = $.NSPasteboard.generalPasteboard;
pasteboard.clearContents;
if (!pasteboard.setStringForType(message, $.NSPasteboardTypeString)) {
  throw new Error("failed to update the macOS clipboard");
}
'
printf 'Copied Slack message to clipboard.\n'
