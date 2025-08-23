"""
RunPod management module for controlling RunPod instances.
Provides functionality to manage RunPod pods (start, stop, resume, terminate).
"""

import os
import runpod
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from .exceptions import (
    ConfigurationError,
    PodManagementError
)

class RunPodManager:
    """
    Manager class for RunPod pod operations.
    
    This class provides methods to control and manage RunPod instances,
    including creating, stopping, resuming, and terminating pods.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        env_file: Optional[str] = None
    ):
        """
        Initialize the RunPod manager.

        Args:
            api_key: RunPod API key. If not provided, will look for RUNPOD_API_KEY in env
            env_file: Path to .env file for configuration
        
        Raises:
            ConfigurationError: If API key is not provided or invalid
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        self.api_key = api_key or os.getenv('RUNPOD_API_KEY')
        
        if not self.api_key:
            raise ConfigurationError(
                "RunPod API key must be provided either through parameters or environment variables"
            )

        # Set the API key for runpod library
        runpod.api_key = self.api_key

    def list_pods(self) -> List[Dict[str, Any]]:
        """
        Get all pods associated with the account.

        Returns:
            List[dict]: List of pod information dictionaries

        Raises:
            PodManagementError: If there's an error retrieving pods
        """
        try:
            return runpod.get_pods()
        except Exception as e:
            raise PodManagementError(f"Failed to list pods: {str(e)}")

    def get_pod(self, pod_id: str) -> Dict[str, Any]:
        """
        Get information about a specific pod.

        Args:
            pod_id: ID of the pod to retrieve

        Returns:
            dict: Pod information

        Raises:
            PodManagementError: If pod cannot be found or accessed
        """
        try:
            return runpod.get_pod(pod_id)
        except Exception as e:
            raise PodManagementError(f"Failed to get pod {pod_id}: {str(e)}")

    def create_pod(
        self,
        name: str,
        image_name: str,
        gpu_type_id: Optional[str] = None,
        instance_id: Optional[str] = None,
        gpu_count: int = 1,
        volume_in_gb: Optional[int] = None,
        container_disk_in_gb: Optional[int] = None,
        ports: Optional[str] = None,
        env: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a new RunPod pod.

        Args:
            name: Name for the pod
            image_name: Docker image to use
            gpu_type_id: GPU type identifier (e.g., "NVIDIA GeForce RTX 3070")
            instance_id: CPU instance type (e.g., "cpu3c-2-4")
            gpu_count: Number of GPUs to allocate
            volume_in_gb: Size of persistent volume in GB
            container_disk_in_gb: Size of container disk in GB
            ports: Port configuration string
            env: List of environment variables as dicts with "key" and "value"

        Returns:
            dict: Created pod information

        Raises:
            PodManagementError: If pod creation fails
            ConfigurationError: If neither gpu_type_id nor instance_id is provided
        """
        if not gpu_type_id and not instance_id:
            raise ConfigurationError("Either gpu_type_id or instance_id must be provided")

        try:
            return runpod.create_pod(
                name=name,
                image_name=image_name,
                gpu_type_id=gpu_type_id,
                instance_id=instance_id,
                gpu_count=gpu_count,
                volume_in_gb=volume_in_gb,
                container_disk_in_gb=container_disk_in_gb,
                ports=ports,
                env=env
            )
        except Exception as e:
            raise PodManagementError(f"Failed to create pod: {str(e)}")

    def stop_pod(self, pod_id: str) -> Dict[str, Any]:
        """
        Stop a running pod.

        Args:
            pod_id: ID of the pod to stop

        Returns:
            dict: Response data from the stop operation

        Raises:
            PodManagementError: If pod cannot be stopped
        """
        try:
            return runpod.stop_pod(pod_id)
        except Exception as e:
            raise PodManagementError(f"Failed to stop pod {pod_id}: {str(e)}")

    def resume_pod(
        self,
        pod_id: str,
        gpu_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Resume a stopped pod.

        Args:
            pod_id: ID of the pod to resume
            gpu_count: Optional number of GPUs to allocate on resume

        Returns:
            dict: Response data from the resume operation

        Raises:
            PodManagementError: If pod cannot be resumed
        """
        try:
            return runpod.resume_pod(pod_id, gpu_count=gpu_count)
        except Exception as e:
            raise PodManagementError(f"Failed to resume pod {pod_id}: {str(e)}")

    def terminate_pod(self, pod_id: str) -> Dict[str, Any]:
        """
        Terminate (permanently delete) a pod.

        Args:
            pod_id: ID of the pod to terminate

        Returns:
            dict: Response data from the terminate operation

        Raises:
            PodManagementError: If pod cannot be terminated
        """
        try:
            return runpod.terminate_pod(pod_id)
        except Exception as e:
            raise PodManagementError(f"Failed to terminate pod {pod_id}: {str(e)}")

    def get_pod_status(self, pod_id: str) -> str:
        """
        Get the current status of a pod.

        Args:
            pod_id: ID of the pod to check

        Returns:
            str: Current pod status

        Raises:
            PodManagementError: If pod status cannot be retrieved
        """
        try:
            pod_info = self.get_pod(pod_id)
            return pod_info.get('desiredStatus', 'UNKNOWN')
        except Exception as e:
            raise PodManagementError(f"Failed to get pod status for {pod_id}: {str(e)}")

    def wait_for_pod_status(
        self,
        pod_id: str,
        desired_status: str,
        timeout: int = 300,
        check_interval: int = 5
    ) -> bool:
        """
        Wait for a pod to reach a desired status.

        Args:
            pod_id: ID of the pod to monitor
            desired_status: Status to wait for (e.g., "RUNNING", "STOPPED")
            timeout: Maximum time to wait in seconds
            check_interval: Time between status checks in seconds

        Returns:
            bool: True if desired status was reached, False if timed out

        Raises:
            PodManagementError: If pod status cannot be checked
        """
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            current_status = self.get_pod_status(pod_id)
            if current_status == desired_status:
                return True
            time.sleep(check_interval)

        return False
