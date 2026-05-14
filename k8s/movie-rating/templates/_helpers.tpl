{{- define "movie-rating.app.env" -}}
{{- range $name, $value := .Values.secrets }}
{{- $name := regexReplaceAll "([a-z])([A-Z])" $name "${1}_${2}" | upper }}
- name: {{ $name }}
  value: {{ $value | quote }}
{{- end -}}
{{- end -}}

{{- define "movie-rating.migrations.env" -}}
{{- range $name, $value := .Values.secrets }}
{{- if ne $name "jwtSecretKey" }}
{{- $name := regexReplaceAll "([a-z])([A-Z])" $name "${1}_${2}" | upper }}
- name: {{ $name }}
  value: {{ $value | quote }}
{{- end }}
{{- end -}}
{{- end -}}
