{{- define "lab-laboratory.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "lab-laboratory.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := include "lab-laboratory.name" . -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "lab-laboratory.labels" -}}
app.kubernetes.io/name: {{ include "lab-laboratory.name" . }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "lab-laboratory.selectorLabels" -}}
app.kubernetes.io/name: {{ include "lab-laboratory.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

