#!/usr/bin/env sh

deploy () {
  case $1 in
    "")
      FILTER="/ghdl /pkg";;
    "base")
      FILTER="/build /run";;
    "ext")
      FILTER="/ext";;
    "synth")
      FILTER="/synth";;
    "vunit")
      FILTER="/vunit";;
    "pkg")
      FILTER="/pkg:all";;
    *)
      FILTER="/";;
  esac

  echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

  echo "IMAGES: $FILTER"
  docker images

  for key in $FILTER; do
    for tag in `echo $(docker images "ghdl$key*" | awk -F ' ' '{print $1 ":" $2}') | cut -d ' ' -f2-`; do
      if [ "$tag" = "REPOSITORY:TAG" ]; then break; fi
      i="`echo $tag | grep -oP 'ghdl/\K.*' | sed 's#:#-#g'`"
      gstart "[DOCKER push] ${tag}" "$ANSI_YELLOW"
      if [ "x$SKIP_DEPLOY" = "xtrue" ]; then
        printf "${ANSI_YELLOW}SKIP_DEPLOY...$ANSI_NOCOLOR\n"
      else
        docker push $tag
      fi
      gend
    done
  done

  docker logout
}
