cookbook_file "/etc/yum.repos.d/nginx.repo" do
  source "nginx/nginx.repo"
  mode 0644
  owner "root"
  group "root"
end
