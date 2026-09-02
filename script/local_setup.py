import subprocess as sub
import os
import yaml


def clone_repo(repo_url:str,target_dir:str, branch_name="develop"):
    if not os.path.exists(target_dir):
        sub.run(["git", "clone", "-b", branch_name, repo_url, target_dir], check=True)
        print(f"Repository cloned on branch '{branch_name}'")
    else:
    # If repo exists, switch branch
        try:
            sub.run(["git", "-C", target_dir, "fetch"], check=True)
            sub.run(["git", "-C", target_dir, "checkout", branch_name], check=True)
            sub.run(["git", "-C", target_dir, "pull"], check=True)
            print(f"Switched to branch '{branch_name}'")
        except sub.CalledProcessError as e:
            print(f"Error switching branch: {e}")
            
def compose_docker(target_dir:str, project_name:str):
    print("Run docker compose....!")
    compose_file = target_dir+"/docker-compose.yml"
    try:
        # Run docker compose up with build
        sub.run(
            ["docker", "compose", "-f", compose_file, "-p", project_name, "up", "-d", "--build"],
            check=True,
            shell=True  # Needed for Windows so PATH resolution works
        )
        print("Docker Compose started successfully!")
    except sub.CalledProcessError as e:
        print(f"Error running Docker Compose: {e}")
        
def build_service(target_dir: str, service: str):
    print(f"Build {service}")
    wrapper = "mvnw.cmd"
    try:
        sub.run(
            [wrapper, "clean", "install", "-Dmaven.test.skip=true", "-f", os.path.join(target_dir, "pom.xml")],
            check=True,
            shell=True
        )
    except sub.CalledProcessError as e:
        print(f"Error running mvn install: {e}")
        
        
def run_service(target_dir:str,jar_name:str,service_name:str, env_file=".env",log_dir="api_logs"):
    print("Load env variables...!")
    __env_vars={}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key,value = line.split("=",1)
                __env_vars[key.strip()]=value.strip()
                
    server_port=__env_vars["server.port"]
    print(f"RUN {service_name} at {server_port}")
                
    # Merge with current environment
    env = {**os.environ, **__env_vars}
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, f"{service_name}_{server_port}.log")

    try:
        # sub.run(["java","-jar",target_dir+"/target/"+jar_name], check=True,shell=True, env=env)
        # Run in background
        run_command:list=["java", "-jar", os.path.join(target_dir, "target", jar_name)]
        
        # Open log file for writing
        with open(log_file_path, "w") as log_file:
            process = sub.Popen(
                run_command,
                env=env,
                stdout=log_file,
                stderr=log_file,
                creationflags=sub.CREATE_NO_WINDOW
            )

        print(f"{service_name} app started at PORT {server_port} in background (PID={process.pid})")
        print(f"Logs are being written to: {log_file_path}")
                
    except sub.CalledProcessError as e:
        print(f"Error while running master service at port {server_port}")
        
        
def main():
    print("Local setup starting........!")

    # Load services from YAML
    with open("config/services.yml", "r") as f:
        config = yaml.safe_load(f)
    services = config["services"]

    for svc in services:
        print(f"\n--- Setting up {svc['project_name']} ---")
        clone_repo(repo_url=svc["repo_url"], target_dir=svc["target_dir"], branch_name=svc["branch_name"])
        compose_docker(target_dir=svc["target_dir"], project_name=svc["project_name"])
        build_service(target_dir=svc["target_dir"], service=svc["project_name"])
        run_service(
            target_dir=svc["target_dir"],
            jar_name=svc["jar_name"],
            service_name=svc["project_name"],
            env_file=svc["env_file"],
            log_dir= svc["log_dir"]
        )
        print(f"{svc['project_name']} running....!")
            
if __name__ == "__main__":
    main()