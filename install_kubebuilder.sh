#!/bin/bash

# Download kubebuilder
curl -L -o kubebuilder "https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH)"

# Make it executable
chmod +x kubebuilder

# Move it to /usr/local/bin/
sudo mv kubebuilder /usr/local/bin/

# Install controller-gen CLI
GO111MODULE=on go install sigs.k8s.io/controller-tools/cmd/controller-gen@latest


echo "Kubebuilder installed successfully."

