ports = {
	'tcp': {
{{ range $key, $value := . }}{{ range $i, $address := $value.Addresses }}{{ if eq $address.Proto "tcp" }}
    {{ if eq $address.HostIP "0.0.0.0" }}
		'{{ $address.HostPort }}': {
			"iptables": "{{ $address.IP }}:{{ $address.Port }}",
			"ip6tables": "[{{ $address.IP6Global }}]:{{ $address.Port }}",
		},
    {{ end }}
{{ end }}{{ end }}{{ end }}
	},
	'udp': {
{{ range $key, $value := . }}{{ range $i, $address := $value.Addresses }}{{ if eq $address.Proto "udp" }}
    {{ if eq $address.HostIP "0.0.0.0" }}
		'{{ $address.HostPort }}': {
			"iptables": "{{ $address.IP }}:{{ $address.Port }}",
			"ip6tables": "[{{ $address.IP6Global }}]:{{ $address.Port }}",
		},
    {{ end }}
{{ end }}{{ end }}{{ end }}
	}
}
