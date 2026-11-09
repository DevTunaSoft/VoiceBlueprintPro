#!/bin/sh
set -eu
IOS_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ROOT=$(CDPATH= cd -- "$IOS_DIR/../.." && pwd)
SHERPA_ONNX_LIBRARY=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$ROOT/mobile/native/ios/build/macos/runtime-paths.json" 'sherpa-onnx')
VOICEBLUEPRINT_LIBRARY=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$ROOT/mobile/native/ios/build/macos/runtime-paths.json" 'omnivoice.cpp')
LLAMA_LIBRARY=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$ROOT/mobile/native/ios/build/macos/runtime-paths.json" 'llama.cpp')
export SHERPA_ONNX_LIBRARY VOICEBLUEPRINT_LIBRARY LLAMA_LIBRARY
export VOICEBLUEPRINT_REAL_AUX=1
# Native engines are memory intensive; keep these real workflows sequential.
"$IOS_DIR/scripts/check-swift.sh" test --filter realAuxiliaryCloneAndTranslation
"$IOS_DIR/scripts/check-swift.sh" test --filter realAuxiliaryPhoneVoiceCreationAndSpeak
exec "$IOS_DIR/scripts/check-swift.sh" test --filter realAuxiliaryPhoneDubOfflineAndResume
