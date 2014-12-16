package "python-virtualenv" do
    action :install
    options "--force-yes"
end

package "postgresql-server-dev-9.3" do
    action :install
    options "--force-yes"
end

package "python-dev" do
    action :install
    options "--force-yes"
end
