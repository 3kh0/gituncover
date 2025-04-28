from colorama import Fore, init
from events import l1, l2
from keys import fetch_ssh, fetch_gpg

init(autoreset=True)

def main():
    username = input("github username: ")
    try:
        print(Fore.BLUE + f"pulling events for {username}...")
        events = l1(username)
        email_data, truncated = l2(events)
        if email_data:
            print(Fore.GREEN + "done! here are the emails and commits that were found:")
            for email, commits in email_data.items():
                print(Fore.CYAN + f"\nemail: {email}")
                truncatedc = truncated.get(email, {})
                for commit in commits:
                    merge_flag = Fore.RED + commit['is_merge'] if commit['is_merge'] else ""
                    print(
                        Fore.YELLOW + f"  - {commit['repo']} | "
                        f"{Fore.WHITE}{commit['url']} {merge_flag}"
                    )
                for repo, truncated_count in truncatedc.items():
                    print(Fore.MAGENTA + f"    (truncated {truncated_count} commits from {repo})")
        else:
            print(Fore.RED + "no emails or repositories found in public events :(")

        ssh_keys = fetch_ssh(username)
        if ssh_keys:
            print(Fore.GREEN + "done! here are the ssh keys that were found:")
            for key in ssh_keys:
                print(Fore.YELLOW + f"  - {key}")
        else:
            print(Fore.RED + f"no ssh keys found for {username}.")

        gpg_keys = fetch_gpg(username)
        if gpg_keys["raw_key"]:
            print(Fore.GREEN + "done! here are the gpg keys that were found:")
            #print(Fore.YELLOW + "Raw Key:")
            #print(Fore.WHITE + gpg_keys["raw_key"])
            print(Fore.YELLOW + "metadata:")
            for key, value in gpg_keys["metadata"].items():
                print(Fore.WHITE + f"  {key}: {value}")
        else:
            print(Fore.RED + f"no gpg keys found for {username}.")

    except Exception as e:
        print(Fore.RED + f"error: {e}")

if __name__ == "__main__":
    main()