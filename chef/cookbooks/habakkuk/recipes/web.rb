cookbook_file "/etc/yum.repos.d/nginx.repo" do
  source "nginx/nginx.repo"
  mode 0644
  owner "root"
  group "root"
end

package "nginx" do
    :upgrade
end

cookbook_file "/etc/nginx/sites-enabled/bakkify" do
  source "nginx/bakkify"
  mode 0640
  owner "root"
  group "root"
  notifies :restart, resources(:service => "nginx")
end
