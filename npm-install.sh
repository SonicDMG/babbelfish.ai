#!/bin/sh

set -eux -o pipefail

(cd components &&
npm install --prefix elevenlabs_component/frontend && npm run build --prefix elevenlabs_component/frontend &&
npm install --prefix audio_component/frontend && npm run build --prefix audio_component/frontend)

