"""
Governance Module for GETS Compliance Studio
Programmatic interface for jurisdiction-aware compliance management
"""

import yaml
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union


class EmpowermentDashboard:
    """
    Programmatic interface for compliance governance operations.
    Enables visibility control, data export, and policy management.
    """
    
    def __init__(self, config_dir: str = "."):
        """
        Initialize the Empowerment Dashboard.
        
        Args:
            config_dir: Directory containing policy_profiles.yaml and loader_config.yaml
        """
        self.config_dir = Path(config_dir)
        self.policies = self._load_policies()
        self.loader_config = self._load_loader_config()
        self.visibility_mode = "global"  # global, local, regional
        
    def _load_policies(self) -> Dict:
        """Load policy profiles from YAML."""
        policy_file = self.config_dir / "policy_profiles.yaml"
        if not policy_file.exists():
            raise FileNotFoundError(f"Policy profiles not found at {policy_file}")
        
        with open(policy_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_loader_config(self) -> Dict:
        """Load media loader configuration from YAML."""
        loader_file = self.config_dir / "loader_config.yaml"
        if not loader_file.exists():
            raise FileNotFoundError(f"Loader config not found at {loader_file}")
        
        with open(loader_file, 'r') as f:
            return yaml.safe_load(f)
    
    def toggle_visibility(self, mode: str) -> None:
        """
        Toggle dashboard visibility mode.
        
        Args:
            mode: One of 'global', 'local', 'regional'
                - global: Show all jurisdictions
                - local: Show single jurisdiction (based on current context)
                - regional: Show regional groupings (EU, Asia-Pacific, Americas)
        """
        valid_modes = ['global', 'local', 'regional']
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of {valid_modes}")
        
        self.visibility_mode = mode
        print(f"✓ Visibility mode set to: {mode}")
        
        if mode == "local":
            print("  → Showing single jurisdiction context")
        elif mode == "regional":
            print("  → Showing regional groupings")
        else:
            print("  → Showing all jurisdictions")
    
    def export_summary(self, filename: str, format: str = "csv") -> None:
        """
        Export compliance summary to file.
        
        Args:
            filename: Output filename (e.g., 'summary.csv')
            format: Export format ('csv', 'json', 'yaml')
        """
        summary_data = self._generate_summary()
        
        output_path = Path(filename)
        
        if format == "csv" or filename.endswith('.csv'):
            df = pd.DataFrame(summary_data)
            df.to_csv(output_path, index=False)
            print(f"✓ Summary exported to: {output_path} (CSV format)")
            
        elif format == "json" or filename.endswith('.json'):
            import json
            with open(output_path, 'w') as f:
                json.dump(summary_data, f, indent=2)
            print(f"✓ Summary exported to: {output_path} (JSON format)")
            
        elif format == "yaml" or filename.endswith('.yaml') or filename.endswith('.yml'):
            with open(output_path, 'w') as f:
                yaml.dump(summary_data, f, default_flow_style=False)
            print(f"✓ Summary exported to: {output_path} (YAML format)")
            
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_summary(self) -> List[Dict]:
        """Generate compliance summary data."""
        summary = []
        profiles = self.policies.get('profiles', {})
        
        for profile_name, profile_data in profiles.items():
            requirements = profile_data.get('requirements', {})
            penalties = profile_data.get('penalties', {})
            
            summary.append({
                'profile': profile_name,
                'jurisdiction': profile_data.get('jurisdiction', 'Unknown'),
                'regulator': profile_data.get('regulator', 'Unknown'),
                'layer': profile_data.get('layer', 'N/A'),
                'enforcement_priority': profile_data.get('enforcement_priority', 'medium'),
                'max_fine': penalties.get('max_fine', 'N/A'),
                'age_limits': requirements.get('age_limits', 'N/A'),
                'content_moderation': requirements.get('content_moderation', 'N/A'),
                'transparency': requirements.get('transparency', 'N/A'),
                'data_protection': requirements.get('data_protection', 'N/A'),
            })
        
        return summary
    
    def get_profile(self, profile_name: str) -> Dict:
        """
        Get specific policy profile.
        
        Args:
            profile_name: Profile identifier (e.g., 'UK_OSA_v1')
            
        Returns:
            Profile configuration dictionary
        """
        profiles = self.policies.get('profiles', {})
        if profile_name not in profiles:
            raise ValueError(f"Profile '{profile_name}' not found")
        
        return profiles[profile_name]
    
    def list_profiles(self) -> List[str]:
        """List all available policy profiles."""
        return list(self.policies.get('profiles', {}).keys())
    
    def get_media_rules(self, media_type: str, profile_name: str) -> Dict:
        """
        Get media access rules for specific media type and jurisdiction.
        
        Args:
            media_type: Media type (video, book, scenario, trailer, podcast)
            profile_name: Jurisdiction profile (e.g., 'UK_OSA_v1')
            
        Returns:
            Media rules dictionary
        """
        media_types = self.loader_config.get('media_types', {})
        
        if media_type not in media_types:
            raise ValueError(f"Media type '{media_type}' not found")
        
        jurisdiction_rules = media_types[media_type].get('controls', {}).get('jurisdiction_rules', {})
        
        if profile_name not in jurisdiction_rules:
            # Return default behavior
            return self.loader_config.get('default_behavior', {}).get('unknown_jurisdiction', {})
        
        return jurisdiction_rules[profile_name]
    
    def check_media_access(self, media_type: str, profile_name: str, user_age: int) -> Dict:
        """
        Check if media access is allowed for given parameters.
        
        Args:
            media_type: Media type to check
            profile_name: Jurisdiction profile
            user_age: User's age
            
        Returns:
            Access decision dictionary with 'allowed', 'reason', and 'rules' keys
        """
        rules = self.get_media_rules(media_type, profile_name)
        
        access_status = rules.get('access', 'allowed')
        min_age = rules.get('min_age', 0)
        
        # Check if disabled
        if access_status == 'disabled':
            return {
                'allowed': False,
                'reason': f'{media_type} is disabled in this jurisdiction',
                'rules': rules
            }
        
        # Check age requirement
        if min_age and user_age < min_age:
            return {
                'allowed': False,
                'reason': f'Age requirement not met (requires {min_age}+, user is {user_age})',
                'rules': rules
            }
        
        # Access granted
        status = 'restricted' if access_status == 'restricted' else 'allowed'
        return {
            'allowed': True,
            'status': status,
            'reason': f'Access {status} - all requirements met',
            'rules': rules
        }
    
    def get_resolution_rules(self) -> Dict:
        """Get jurisdiction resolution rules."""
        return self.policies.get('resolution_rules', {})
    
    def get_audit_config(self) -> Dict:
        """Get audit logging configuration."""
        return self.policies.get('audit_logging', {})
    
    def generate_compliance_report(self, profile_names: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Generate detailed compliance report.
        
        Args:
            profile_names: List of profiles to include (None = all profiles)
            
        Returns:
            DataFrame with compliance details
        """
        summary = self._generate_summary()
        df = pd.DataFrame(summary)
        
        if profile_names:
            df = df[df['profile'].isin(profile_names)]
        
        return df
    
    def get_media_matrix(self) -> pd.DataFrame:
        """
        Generate media access matrix across all jurisdictions.
        
        Returns:
            DataFrame showing access status for each media type per jurisdiction
        """
        media_types = self.loader_config.get('media_types', {})
        profiles = list(self.policies.get('profiles', {}).keys())[:7]  # Top 7 profiles
        
        matrix_data = []
        
        for media_type in media_types.keys():
            row = {'media_type': media_type}
            jurisdiction_rules = media_types[media_type].get('controls', {}).get('jurisdiction_rules', {})
            
            for profile in profiles:
                rules = jurisdiction_rules.get(profile, {})
                access = rules.get('access', 'allowed')
                min_age = rules.get('min_age', '-')
                
                if access == 'disabled':
                    status = "disabled"
                elif access == 'restricted':
                    status = f"restricted ({min_age}+)" if min_age != '-' else "restricted"
                else:
                    status = f"allowed ({min_age}+)" if min_age != '-' else "allowed"
                
                row[profile] = status
            
            matrix_data.append(row)
        
        return pd.DataFrame(matrix_data)
    
    def __repr__(self) -> str:
        """String representation of the dashboard."""
        num_profiles = len(self.policies.get('profiles', {}))
        num_media_types = len(self.loader_config.get('media_types', {}))
        return f"<EmpowermentDashboard: {num_profiles} profiles, {num_media_types} media types, mode={self.visibility_mode}>"


# Example usage
if __name__ == "__main__":
    # Initialize dashboard
    dashboard = EmpowermentDashboard()
    
    # Toggle visibility
    dashboard.toggle_visibility("local")
    
    # Export summary
    dashboard.export_summary("summary.csv")
    
    # Get specific profile
    uk_profile = dashboard.get_profile("UK_OSA_v1")
    print(f"\nUK Profile: {uk_profile['jurisdiction']}")
    
    # Check media access
    access = dashboard.check_media_access("video", "AU_Ban_v1", user_age=15)
    print(f"\nAU Video Access (age 15): {access['allowed']} - {access['reason']}")
    
    # Generate compliance report
    report = dashboard.generate_compliance_report()
    print(f"\nCompliance Report:\n{report.head()}")
    
    # Get media matrix
    matrix = dashboard.get_media_matrix()
    print(f"\nMedia Access Matrix:\n{matrix}")
